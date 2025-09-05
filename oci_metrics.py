#!/usr/bin/env python3
import oci
from datetime import datetime, timezone, timedelta
import json
import argparse
import sys
import itertools, threading , time

from openpyxl import Workbook

def spinner():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if getattr(spinner, "stop", False):
            break
        sys.stdout.write('\rFetching metrics from oci ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\rDone!        \n")


def get_metric_value(monitoring_client, namespace, query, compartment_id, start_seconds=300, end_seconds=0):
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(seconds=start_seconds)
    end_time = now - timedelta(seconds=end_seconds)
    try:
        response = monitoring_client.summarize_metrics_data(
            compartment_id=compartment_id,
            summarize_metrics_data_details=oci.monitoring.models.SummarizeMetricsDataDetails(
                namespace=namespace,
                query=query,
                start_time=start_time,
                end_time=end_time,
                resolution="1m"
            )
        )
        if response.data and response.data[0].aggregated_datapoints:
            latest = response.data[0].aggregated_datapoints[-1]
            return float(latest.value)
    except Exception:
        return 0.0
    return 0.0

def main():
    parser = argparse.ArgumentParser(description="Fetch OCI Compute Metrics for instances")
    parser.add_argument("-c", "--config-profile", default="DEFAULT", help="OCI config profile name")
    parser.add_argument("-i", "--input", default="all_instances.txt", help="File with instance OCIDs")
    parser.add_argument("-o", "--output-json", default="oci_metrics_output.json", help="Output JSON file")
    parser.add_argument("-x", "--output-xlsx", default="oci_metrics_output.xlsx", help="Output Excel file")
    args = parser.parse_args()

    try:
        config = oci.config.from_file("~/.oci/config", args.config_profile)
    except Exception as e:
        print(f"Failed to load OCI config: {e}")
        sys.exit(1)

    compute_client = oci.core.ComputeClient(config)
    monitoring_client = oci.monitoring.MonitoringClient(config)

    try:
        with open(args.input, "r") as f:
            instance_ocids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Input file not found: {args.input}")
        sys.exit(1)

    all_instances_data = []

    for instance_ocid in instance_ocids:
        try:
            instance = compute_client.get_instance(instance_ocid).data
            compartment_id = instance.compartment_id
            agent_plugins = {p.name: getattr(p, "desired_state", None) for p in instance.agent_config.plugins_config}
            agent_desired = agent_plugins.get("Compute Instance Monitoring", "DISABLED")

            cpu_query = f'CpuUtilization[1m]{{resourceId="{instance_ocid}"}}.mean()'
            memory_query = f'MemoryUtilization[1m]{{resourceId="{instance_ocid}"}}.mean()'

            cpu_value = get_metric_value(monitoring_client, "oci_computeagent", cpu_query, compartment_id)
            memory_value = get_metric_value(monitoring_client, "oci_computeagent", memory_query, compartment_id)

            if agent_desired == "ENABLED":
                if cpu_value > 0 or memory_value > 0:
                    oracle_agent_status = "RUNNING"
                else:
                    oracle_agent_status = "ENABLED but not running"
            else:
                oracle_agent_status = "DISABLED"

            instance_data = {
                "Name": instance.display_name,
                "OCID": instance.id,
                "UsageOCPU": f"{cpu_value:.2f}%",
                "UsageMemory": f"{memory_value:.2f}%",
                "OracleAgent": oracle_agent_status,
                "MachineStatus": instance.lifecycle_state,
                "UATTime": datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            }

            all_instances_data.append(instance_data)

        except Exception as e:
            print(f"Error fetching data for {instance_ocid}: {e}")

    # Save JSON output
    with open(args.output_json, "w") as f:
        json.dump(all_instances_data, f, indent=2)
    print(f"JSON output saved to {args.output_json}")

    # Save Excel output
    wb = Workbook()
    ws = wb.active
    ws.title = "OCI Metrics"
    headers = ["Name", "OCID", "UsageOCPU", "UsageMemory", "OracleAgent", "MachineStatus", "UATTime"]
    ws.append(headers)

    for data in all_instances_data:
        ws.append([data[h] for h in headers])

    wb.save(args.output_xlsx)
    print(f"Excel output saved to {args.output_xlsx}")

if __name__ == "__main__":
    t=threading.Thread(target=spinner)
    t.start()
    try:
        main()
    finally:
        spinner.stop = True
        t.join()
