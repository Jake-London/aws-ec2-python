import boto3
import csv
import paramiko
import time

def show_instances(status, ec2):
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name','Values': [status]}])
    for inst in instances:
        print(inst.id, inst.instance_type, inst.image_id, inst.public_ip_address)

def run_command(cmd, ssh):
    print("Running command: " + cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    if (exit_status == 0):
        print("Completed")
    stdout.readlines()

def get_csv(filename):
    temp = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for idx, row in enumerate(reader):
            if (idx == 0):
                continue
            else:
                temp.append(row)
            
    return temp

def amazon_linux_install_docker(ssh):
    run_command("sudo yum update -y", ssh)
    run_command("sudo amazon-linux-extras install docker", ssh)
    run_command("sudo yum install docker", ssh)
    run_command("sudo service docker start", ssh)
    run_command("sudo usermod -a -G docker ec2-user", ssh)

def ubuntu_lts_install_docker(ssh):
    run_command("sudo apt-get update", ssh)
    run_command("sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common -y", ssh)
    run_command("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -", ssh)
    run_command("sudo apt-key fingerprint 0EBFCD88", ssh)
    run_command("sudo add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\"", ssh)
    run_command("sudo apt-get update", ssh)
    run_command("sudo apt-get install docker-ce docker-ce-cli containerd.io -y", ssh)

def main():
    print("Creating ec2 connection")
    ec2 = boto3.resource('ec2')


    templates = get_csv('template.csv')
    instances = get_csv('instances.csv')
    containers = get_csv('container.csv')

    """ print(templates)
    print(instances)
    print(container) """

    instances_info = []

    for idx, instance in enumerate(instances):
        for template in templates:
            if (template[0] == instance[0]):
                temp = {}
                temp.update({'image_id': template[1]})
                temp.update({'image_type': template[2]})
                temp.update({'image_size': template[3]})
                temp.update({'image_secu': template[4]})
                temp.update({'image_regn': template[5]})
                temp.update({'image_cont': instance[3]})
                temp.update({'image_name': instance[1]})
                temp.update({'image_keys': instance[2]})
                temp.update({'image_temp': instance[0]})
                if (instance[0] == 'Amazon Linux 2'):
                    temp.update({'image_voln': '/dev/xvda'})
                    temp.update({'image_user': 'ec2-user'})
                elif (instance[0] == 'Ubuntu Server 20.04 LTS'):
                    temp.update({'image_voln': '/dev/sda1'})
                    temp.update({'image_user': 'ubuntu'})
                elif (instance[0] == 'Red Hat Enterprise Linux 8' or instance[0] == 'SUSE Linux Enterprise Server 15 SP2'):
                    temp.update({'image_voln': '/dev/sda1'})
                    temp.update({'image_user': 'ec2-user'})
                else:
                    temp.update({'image_voln': ''})
                    temp.update({'image_user': ''})
                instances_info.append(temp)
                break

    """ print(instances_info[0]) """
    
    for instance in instances_info:
        
        

        print("Attempting to start instance with template: " + instance['image_temp'])
        """ if (instance['image_temp'] == 'Amazon Linux 2'):
            continue """
        if (instance['image_voln'] != '' and instance['image_size'] != ''):
            i = ec2.create_instances(
                ImageId=instance['image_id'],
                MinCount=1,
                MaxCount=1,
                InstanceType=instance['image_type'],
                KeyName=instance['image_keys'],
                SecurityGroups=[
                    instance['image_secu']
                ],
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': instance['image_name']
                            }
                        ]
                    }
                ],
                BlockDeviceMappings=[
                    {
                        'DeviceName': instance['image_voln'],
                        'Ebs': {
                            'VolumeSize': int(instance['image_size'])
                        }
                    }
                ]
            )[0]
        else:
            i = ec2.create_instances(
                ImageId=instance['image_id'],
                MinCount=1,
                MaxCount=1,
                InstanceType=instance['image_type'],
                KeyName=instance['image_keys'],
                SecurityGroups=[
                    instance['image_secu']
                ],
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': instance['image_name']
                            }
                        ]
                    }
                ]
            )[0]

        print("Instance created")
        i.wait_until_running()
        print("Instance started and running")
        i.reload()

        i2 = ec2.Instance(i.id)
        ip = i2.public_ip_address
        k = paramiko.RSAKey.from_private_key_file(instance['image_keys'] + ".pem")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print("Attempting to connect to server via ssh: " + ip)

        time.sleep(5)
        
        while (1):
            if (instance['image_user'] == ''):
                break
            try:
                ssh.connect(ip, username=instance['image_user'], pkey=k)
                break
            except paramiko.ssh_exception.NoValidConnectionsError as e:
                print("...")
                time.sleep(2)
            except paramiko.ssh_exception.AuthenticationException as e:
                print("Unable to establish ssh connection")
            except paramiko.ssh_exception.SSHException as e:
                print("...")
                time.sleep(2)
            
        print("Connected to instance")
            
        if (instance['image_temp'] == 'Amazon Linux 2'):
            amazon_linux_install_docker(ssh)
            """ run_command("sudo yum install git -y", ssh)
            run_command("git clone https://github.com/Jake-London/portfolio.git", ssh) """

        elif (instance['image_temp'] == 'Ubuntu Server 20.04 LTS'):
            ubuntu_lts_install_docker(ssh)

        run_command("mkdir webcontent", ssh)
        
        if (instance['image_user'] != ''):
            ftp = ssh.open_sftp()
            ftp.put('index.html', '/home/' + instance['image_user'] + '/webcontent/index.html')
            time.sleep(1)
            ftp.put('Dockerfile', '/home/' + instance['image_user'] + '/webcontent/Dockerfile')
        
        for container in containers:
            if (instance['image_cont'] == container[0]):
                if (container[2] == 'Docker hub'):
                    try:
                        script = container[3]
                    except:
                        script = ''
                
                    if (script != ''):
                        print(script)
                        ftp.put(script, '/home/' + instance['image_user'] + '/webcontent/' + script)
                        run_command("cd webcontent; chmod +x " + script, ssh)
                        run_command("cd webcontent; sudo sh " + script, ssh)
                    elif (script == ''):
                        run_command("sudo docker pull " + container[1], ssh)

        

        ftp.close()
        ssh.close()

    show_instances('running', ec2)
    

main()