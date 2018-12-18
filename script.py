import googleapiclient.discovery
import json
import time, sys

def main():
  compute = googleapiclient.discovery.build('compute', 'v1')
  project = "reechar-delete-network"
  network = "default"
  deleteNetwork(compute, project, network)

def deleteNetwork(compute, project, network):
  firewalls = getFirewalls(compute, project, network)
  operations = deleteFirewalls(compute, project, firewalls)
  success = waitForOperations(compute, project, operations)
  if success:
    print "Attempting to delete VPC: " + network
    operation = compute.networks().delete(project=project, network=network).execute()
    deleted = waitForOperations(compute, project, [operation["name"]])
    if deleted:
      print "Deleted VPC: " + network
  else:
    print "Something went wrong"

def getFirewalls(compute, project, network):
  result = compute.firewalls().list(project=project, filter="network=\"https://www.googleapis.com/compute/v1/projects/"+project+"/global/networks/"+network+"\"").execute()
  if 'items' in result:
    return map(getFirewallName, result["items"])
  else:
    return []

def getFirewallName(n):
  return n["name"]

def deleteFirewalls(compute, project, firewalls):
  if len(firewalls) <1:
    return []
  print "Attempting to delete " + str(len(firewalls)) + " firewalls"
  operations = []
  for firewall in firewalls:
    operation = deleteFirewall(compute, project, firewall)
    operations.append(operation)
  return operations

def deleteFirewall(compute, project, firewall):
  print "Deleting firewall rule: " + firewall
  result = compute.firewalls().delete(project=project, firewall=firewall).execute()
  operation = result["name"]
  return operation

def waitForOperations(compute, project, operations):
  operationsToCheck = operations
  dotCounter = 0
  while len(operationsToCheck) > 0:
    sys.stdout.write("\r" + "Waiting on "  + str(len(operationsToCheck))
     + ( " operation" if len(operationsToCheck) == 1 else " operations")
     + " to complete" + "."*dotCounter +"   ")
    sys.stdout.flush()
    operation = operationsToCheck.pop()
    result = compute.globalOperations().get(project=project, operation=operation).execute()
    if result['status'] != 'DONE':
      operationsToCheck.append(operation)
    time.sleep(1)
    dotCounter+=1
    if dotCounter > 3:
      dotCounter = 0
  sys.stdout.write("\r                                                       \n")
  sys.stdout.flush
  return True

main()


