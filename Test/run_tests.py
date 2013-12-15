#!/usr/bin/env python3
import subprocess,os,shutil

if os.path.exists("Results"): shutil.rmtree("Results")
	
def run(*args):
	args_ = [os.path.join(blender_dir,"blender.exe"), "-b"]
	args_.extend(args)
	args_.extend(["--", logdir])
	ret = subprocess.call(args_, stdout = log, stderr = subprocess.STDOUT)
	if ret != 0:
		print("\tExit code",ret)
		print("\a")

for blender_dir in ["C:/blender-2.66a-windows64","C:/blender-2.69-windows64"]:
	logdir = os.path.join("Results",blender_dir.split("/")[-1]) 
	if not os.path.exists(logdir): os.makedirs(logdir)
	
	for path,subdirs,files in os.walk("Tests"):
		for blend in files:
			if not blend.endswith(".blend"): continue
			print("Running test",blender_dir,blend)
			logpath = os.path.join(logdir,"{}.txt".format(blend.split(".")[0]))
			with open(logpath,'wb') as log:
				run(os.path.join(path,blend), "-P", "tests\\export_tests.py")
		break
	with open(os.path.join(logdir,"import.txt"),'wb') as log:
		print("Running test",blender_dir,"Import")
		run("-P", "Tests\\import_test.py")
