import os
import subprocess

# Change the current directory
os.chdir('/Users/robertshear/temp/manifest')

# Get the list of remote branches
branches = subprocess.check_output(['git', 'branch', '-r']).decode().splitlines()
output_lines = []

# Loop through each remote branch
for branch in branches:
    # Remove the "origin/" prefix from the branch name
    branch_name = branch.split('origin/')[1]
    
    # Check if the branch name matches the format "RELEASE_x_y"
    if branch_name.startswith('RELEASE_') and len(branch_name.split('_')) == 3:
        # Extract the x and y values from the branch name
        x, y = branch_name.split('_')[1:]
        version_number = f"{x}.{y}"

        # Perform your desired operations on each branch
        print(f"Processing branch: {branch} / {branch_name} / {version_number}")
        
        subprocess.Popen(['git', 'checkout', branch]).wait()
        
        # Loop through all files with .txt extension in the current directory
        for file in os.listdir('.'):
            if file.endswith('.txt'):
                # Extract the filename without the extension
                filename = os.path.splitext(file)[0]
                # Open the file for reading
                with open(file, 'r') as f:
                    # Loop through each line in the file
                    for line in f:
                        # Process each line
                        if line.strip().startswith('Package:'):
                            identifier = line.strip().split('Package:')[1].strip()

                            # ...

                            # Loop through all files with .txt extension in the current directory
                            for file in os.listdir('.'):
                                if file.endswith('.txt'):
                                    # Extract the filename without the extension
                                    filename = os.path.splitext(file)[0]
                                    # Open the file for reading
                                    with open(file, 'r') as f:
                                        # Loop through each line in the file
                                        for line in f:
                                            # Process each line
                                            if line.strip().startswith('Package:'):
                                                identifier = line.strip().split('Package:')[1].strip()
                                                output_lines.append(f"{version_number}|{filename}|{identifier}\n")

# Write all the lines to a single output file
with open('manifest_records.txt', 'w') as output_file:
    output_file.writelines(output_lines)
                
