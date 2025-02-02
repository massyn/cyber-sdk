from cyberlibrary import CyberLibrary
import whois
import datetime

def main(domains):
    M = CyberLibrary()

    M.metric(
        metric_id = 'dns_domain_expity',
        title     = "Domains not expiring in the next 30 days",
        category  = "Governance",
        slo       = 1.00,
        slo_min   = 0.90,
        weight    = 0.5
    )

    days = 30
    for domain in domains:
        expiration_date = whois.whois(domain).expiration_date
        if expiration_date == None:
            compliance = 0
            detail = "Domain does not exist"
        else:
            if datetime.datetime.today() <= expiration_date <= datetime.datetime.today() + datetime.timedelta(days=days):
                compliance = 0
                detail = f"Domain will in the next {days} days on {expiration_date}.  Renew it!"
            else:
                compliance = 1
                detail = f"Domain will expire on {expiration_date}"
        
        M.add(
            resource = domain,
            compliance = compliance,
            detail = detail
        )

    # == show us the score - useful for when we develop and want to test it
    M.summary()

    # == if you want to see the detail of what was produced, this can be handy
    #import tabulate
    #print(tabulate.tabulate(M.data,headers="keys"))

    M.publish() # -- send to the dashboard

main([
    'massyn.net',
    'massyn.com',
    'massyn.co.za',
    'awssecurity.info',
    'ismsowner.com',
    'some-obsure-domain-that-doesnt-exist.never'
])