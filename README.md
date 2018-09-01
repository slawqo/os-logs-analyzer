# os-logs-analyzer
Small scripts to help analyze OpenStack logs files

## Analyze ReST API calls
Script `rest_calls_time.py` can parse and print summary of ReST API calls from
logs file.

Usage example:
```
    ./rest_calls_time.py neutron-server.log
```

Results examle:
```
+-------------------------------------------------------------------------+--------------------+----------------------+--------------------+
|                                 Requests                                | Number of requests | Average request time | Total request time |
+-------------------------------------------------------------------------+--------------------+----------------------+--------------------+
|                   GET /v2.0/auto-allocated-topology/*                   |         4          |     47.489018275     |    189.9560731     |
|                 PUT /v2.0/routers/*/add_router_interface                |         64         |    9.19863867187     |     588.712875     |
|               PUT /v2.0/routers/*/remove_router_interface               |         60         |    7.96093252667     |    477.6559516     |
|                          POST /v2.0/floatingips                         |         48         |    6.88826574167     |    330.6367556     |
|                         PUT /v2.0/floatingips/*                         |         40         |     5.0823248525     |    203.2929941     |
|                           PUT /v2.0/routers/*                           |         26         |    4.24821291154     |    110.4535357     |
|                            POST /v2.0/routers                           |         80         |     3.9501125775     |    316.0090062     |
+-------------------------------------------------------------------------+--------------------+----------------------+--------------------+
```


## Analyze tests results
Script `tests_times.py` can parse and print summary of tests from
`job-output.txt` files.

Usage example:
	./tests_times.py job-output.txt.gz

Results example:
```
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------+-------------+------------+
|                                                                             Test name                                                                              | Test worker | Test result | Test time  |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------+-------------+------------+
|                                tempest.api.compute.servers.test_device_tagging.TaggedBootDevicesTest_v242.test_tagged_boot_devices                                 |      0      |      ok     | 225.618798 |
|                                   tempest.api.compute.servers.test_device_tagging.TaggedBootDevicesTest.test_tagged_boot_devices                                   |      0      |      ok     | 217.35821  |
|                                   tempest.api.compute.volumes.test_attach_volume.AttachVolumeTestJSON.test_attach_detach_volume                                    |      0      |      ok     | 210.323621 |
|                         tempest.api.compute.servers.test_server_personality.ServerPersonalityTestJSON.test_rebuild_server_with_personality                         |      0      |      ok     | 173.880953 |
|                      tempest.api.compute.admin.test_create_server.ServersWithSpecificFlavorTestJSON.test_verify_created_server_ephemeral_disk                      |      3      |      ok     | 168.320289 |
|                                        tempest.scenario.test_network_v6.TestGettingAddress.test_dualnet_multi_prefix_slaac                                         |      0      |      ok     | 161.030555 |
|                       tempest.api.compute.volumes.test_attach_volume.AttachVolumeShelveTestJSON.test_attach_volume_shelved_or_offload_server                       |      2      |      ok     | 155.160813 |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------+-------------+------------+
```
