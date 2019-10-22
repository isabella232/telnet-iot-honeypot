import dns.resolver
import ipaddress
import urllib.parse
import re
import traceback

from backend import ipdb

def filter_ascii(string):
		string = ''.join(char for char in string if ord(char) < 128 and ord(char) > 32 or char in "\r\n ")
		return string

def query_txt(cname):
	try:
		answer = dns.resolver.query(filter_ascii(cname), "TXT")

		for rr in answer.rrset:
			if rr.strings: return rr.strings[0]
	except Exception as e:
		traceback.print_exc()
		pass

	return None

def query_a(cname):
	try:
		answer = dns.resolver.query(filter_ascii(cname), "A")

		for data in answer:
			if data.address: return data.address
	except:
		traceback.print_exc()
		pass

	return None

def txt_to_ipinfo(txt):
	parts = txt.split("|")

	return {
		"asn":     filter_ascii(parts[0].strip()),
		"ipblock": filter_ascii(parts[1].strip()),
		"country": filter_ascii(parts[2].strip()),
		"reg":     filter_ascii(parts[3].strip()),
		"updated": filter_ascii(parts[4].strip())
	}

def txt_to_asinfo(txt):
	parts = txt.split("|")
	
	return {
		"asn":     filter_ascii(parts[0].strip()),
		"country": filter_ascii(parts[1].strip()),
		"reg":     filter_ascii(parts[2].strip()),
		"updated": filter_ascii(parts[3].strip()),
		"name":    filter_ascii(parts[4].strip())
	}

def get_ip4_info(ip):
	oktets  = ip.split(".")
	reverse = oktets[3] + "." + oktets[2] + "." + oktets[1] + "." + oktets[0]
	
	answer = query_txt(reverse + ".origin.asn.cymru.com")

	if answer:
		return txt_to_ipinfo(answer)
	
	return None

def get_ip6_info(ip):
	ip = ipaddress.ip_address(str(ip))
	ip = list(ip.exploded.replace(":", ""))
	
	ip.reverse()
	
	reverse = ".".join(ip)
	
	answer = query_txt(reverse + ".origin6.asn.cymru.com")
	if answer:
		return txt_to_ipinfo(answer)
	
	return None

def get_ip_info(ip):
	is_v4 = "." in ip
	is_v6 = ":" in ip
	
	if is_v4:
		return get_ip4_info(ip)
	elif is_v6:
		return get_ip6_info(ip)
	else:
		print(("Cannot parse ip " + ip))
		return None

def get_asn_info(asn):
	answer = query_txt("AS" + str(asn) + ".asn.cymru.com")
	if answer:
		return txt_to_asinfo(answer)
	
	return None

def get_url_info(url):
	try:
		parsed = urllib.parse.urlparse(url)
		netloc = parsed.netloc
		ip     = None
		
		# IPv6
		if "[" in netloc:
			netloc = re.match("\\[(.*)\\]", netloc).group(1)
			ip = netloc
			
		# IPv4 / domain name
		else:
			if ":" in netloc:
				netloc = re.match("(.*?):", netloc).group(1)
			
			if re.match("[a-zA-Z]", netloc):
				ip = query_a(netloc)
			else:
				ip = netloc
		
		return ip, get_ip_info(ip)
	
	except:
		traceback.print_exc()
		pass
	
	return None

if __name__ == "__main__":
	print(get_ip_info("79.220.249.125"))
	print(get_ip_info("2a00:1450:4001:81a::200e"))
	print(get_asn_info(3320))

	print(get_url_info("http://google.com"))
	print(get_url_info("http://183.144.16.51:14722/.i"))
	print(get_url_info("http://[::1]:14722/.i"))
