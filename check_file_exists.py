import os, sys

models_dir = '/Volumes/Untitled/Resources/aion_assets'

def run():
    with open('test.lst', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')
            filepath = os.path.join(models_dir, line)
            if not os.path.exists(filepath):
                print(line)

if __name__ == '__main__':
    run()
