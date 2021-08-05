import boto3
import datetime

def main():
    ec2 = boto3.resource('ec2')

    instances = ec2.instances.all()

    print('{:<15s} {:<22s} {:<10s} {:<18s} {:<25s}'.format('Instance Name', 'Image ID', 'State', 'Public IP', 'Launch Time'))
    print('---------------------------------------------------------------------------------------------------------')

    for instance in instances:
        """ print(instance.block_device_mappings) """
        if (instance.state['Name'] != 'terminated'):
            print('{:<15s} {:<22s} {:<10s} {:<18s} {}'.format(instance.tags[0]['Value'], instance.image_id, instance.state['Name'], instance.public_ip_address, instance.launch_time))


main()