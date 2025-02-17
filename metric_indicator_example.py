from cyberlibrary import CyberLibrary

def main():
    M = CyberLibrary()

    # initialise the metric definition
    M.metric(
        metric_id = 'test_indicator_id',           # required
        title     = "This is the test indicator",
        category  = "Test category",
        indicator = True,
        slo       = 320,
        slo_min   = 200,
        weight    = 0.5
    )

    # == add the individual tests
    M.add(
        resource = "HostA",
        compliance = 1,
        detail = "Host A is compliant",
        
        # datestamp = "2025-01-02"  # In YYYY-MM-DD format
        # if you wanted to add the dimensions
        business_unit = "Sales"
    )
    M.add(
        resource = "HostB",
        compliance = 1,
        detail = "Host B is compliant"
    )
    M.add(
        resource = "HostC",
        compliance = 0,
        detail = "Host C is not compliant"
    )

    #M.summary()
    # == push the data to the dashboard
    M.publish()


main()