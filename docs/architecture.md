# LSFL Production Architecture

## High-Level Architecture

```text
                         INTERNET
                             |
                             v
                    +------------------+
                    | Customer Portal  |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |    API Gateway   |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
        +-----------+  +-----------+  +-----------+
        |   Order   |  | Inventory |  |  Payment  |
        |  Service  |  |  Service  |  |  Service  |
        +-----+-----+  +-----+-----+  +-----+-----+
              |              |              |
              +--------------+--------------+
                             |
                             v
                    +------------------+
                    |    Database      |
                    +------------------+

                  OPERATIONS LAYER
                  -----------------

        +-------------+    +-------------+
        |  Monitoring |--->|   Alerts    |
        +-------------+    +------+------+
                                  |
                                  v
                         +----------------+
                         | Infrastructure |
                         |   Operations   |
                         +-------+--------+
                                 |
                    +------------+------------+
                    |            |            |
                    v            v            v
                Runbooks    Automation    Incidents
q
