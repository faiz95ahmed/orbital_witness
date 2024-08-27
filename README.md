# Instructions
Build with docker and run with `docker run -p HOST_PORT:8000 <IMAGE_ID>`

# API Reference
Access at `http://localhost:HOST_PORT`
## /entries/ (POST)
Refer to the json file you provided me with. Sample below
```
[
    ...,
    {
        "leaseschedule": {
            "scheduleType": "SCHEDULE OF NOTICES OF LEASE",
            "scheduleEntry": [
                ...,
                {
                    "entryNumber": "1",
                    "entryDate": "",
                    "entryType": "Schedule of Notices of Leases",
                    "entryText": [
                        "21.11.1996      Transformer Site, Manor       16.09.1996      EGL352255  ",
                        "1               Road                          25 years from              ",
                        "16 September               ",
                        "1996                       ",
                        "NOTE 1: See entry in the Charges Register relating to the rights granted by this lease.",
                        "The lease also affects other land",
                        "NOTE 2: No copy of the Lease referred to is held by Land Registry."
                    ]
                },
                ...
            ]
        }
    },
    ...
]
```
returns
```
[
    ...,
    {
        "registrationDate": "21.11.1996",
        "planReference": "1",
        "propertyDescription": "Transformer Site, Manor Road",
        "dateOfLease": "16.09.1996",
        "term": "25 years from 16 September 1996",
        "lesseesTitle": "EGL352255",
        "notes": [
          "NOTE 1: See entry in the Charges Register relating to the rights granted by this lease. The lease also affects other land",
          "NOTE 2: No copy of the Lease referred to is held by Land Registry."
        ]
    },
    ...
]
```
Note that the nested structure of the `leaseschedule`s is not preserved as this was not a requirement in the specification.



# Design Limitations
* Did not implement the PDF functionality
* Some edge cases will not have the columns parsed (only the notes seperated from the rest of the text)
