#from argparse import Action
from pickle import FALSE, NONE
from flask import *
from pytube import YouTube
from moviepy.editor import *
# from selenium import webdriver
from tkinter import filedialog
from tkinter import *
# from pytube.cli import on_progress
# from tqdm import tqdm
# from requests import ConnectionError
# from requests import HTTPError
import moviepy.editor as mp
# import subprocess
# import logging
# import sys
import os
import requests
# import getpass
# import time
# import schedule
# import psutil
# import pathlib
# import shutil
import keyboard
# import pyautogui

import matplotlib
matplotlib.use('TkAgg')

app = Flask(__name__)
#app.config.from_object(__name__)


@app.route("/")
def index():
	return render_template('index.html')


@app.route("/input", methods=['GET'])
def input():
	global video, video_info, video_quality, audio_quality, video_stream, video_itag, audio_itag, youtube_url
	youtube_url = ''
	video_itag = []
	audio_itag = []
	

	if youtube_url == '':
		youtube_url = request.args['inputUrl']	#url을 변수에 저장

	video = YouTube(youtube_url)
	
	video_quality = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
	audio_quality = ['320kbps', '256kbps', '160kbps', '128kbps', '70kbps', '50kbps', '48kbps']
		
	video_result = []
	mp3_result = []

	# 해상도 마다 stream 검사
	video_stream = video_check()
	# 있는 stream 을 페이지에 표시하기 위한 검사 
	for i, stream in enumerate(video_stream): 
		if not stream:
			continue
		video_result.append(video_quality[i])

	audio_stream = mp3_check()
	for i, stream in enumerate(audio_stream):
		if not stream:
			continue
		mp3_result.append(audio_quality[i])

	video_info = {
		"name": video.title, #제목
		"length_min": int(video.length/60), #길이
		"length_sec": video.length-(int(video.length/60)*60),
		"author": video.author, #게시자
		"release": video.publish_date, #게시날짜
		"view": format(video.views, ',d'), #조회수
		"descripton": video.description, #설명
		"thumbnail": video.thumbnail_url, #썸네일
		"url": video.watch_url, #URL
		
		"video_result" : video_result, # 가용 화질
		"mp3_result" : mp3_result, # 가용 오디오 중 최고품질
		
		
	}
	
	
	return render_template('input.html', video_info=video_info)

# download 가능한 stream 검사
def video_check(): 
	video_stream = [] 
	# list 함수 (append)를 사용하기 위해 선언한다 
	# literal 로 선언하면 함수사용 불가 
	# 이거때문에 종나 시간뺏김,,
	
	for i, v in enumerate(video_quality):
		# quality 검사 후 첫번째 stream 가져옴
		temp = video.streams.filter(res=v).first() 
		video_stream.append(temp)
		if not temp:
			# 공백을 붙임
			video_itag.append(None) 
			continue
		# 미춋다... itag 구해왔다... 
		# 선택한 화질을 다운 받을 수 있게 하기 위함 (핸들링)
		video_itag.append(temp.itag) 
		
	
	return video_stream

def mp3_check():
	audio_stream = []

	for i, v in enumerate(audio_quality):
		temp = video.streams.filter(abr=v).first()
		audio_stream.append(temp)
		if not temp:
			audio_itag.append(None)
			continue
		audio_itag.append(temp.itag)

	return audio_stream



@app.route('/down', methods=['GET'])
def down():
	# client -> server 데이터 전송은 form 으로 받을 수 있다
	# 선택한 화질
	quality = request.args.get("quality") 



	# 파일 저장 경로창 정하기 위한 flag 변수
	if "mp3" in quality:
		mp3_flag = 1
	else:
		mp3_flag = 0

	# 파일 저장 경로
	
	dir = save(mp3_flag)
	
	
	# 파일저장 창을 닫았으면
	if dir == '':
		return render_template('cancel.html', video_info=video_info)
	
	# 파일명 정하기 '/' 기준으로 자름
	dir_split = dir.split('/')

	# 자른 리스트 i번째 까지 합침
	file_dir = '/'.join(dir_split[:-1])

	# 디렉토리를 구하고 /를 붙여놔야 파일명만 구할수 있음
	file_dir = file_dir + '/'
	file_name = dir.replace(file_dir, '')

	# mp3 itag 구하는 로직
	# html <option value == "mp3">
	if "mp3" in quality:
		for i, q in enumerate(audio_quality):
			# value 에 붙여놓은 ".mp3" 를 quality랑 합쳐서 검사
			if q + ".mp3" == quality:
				tag = audio_itag[i]
		
		audio_path = video.streams.get_by_itag(tag)
		audio_path = audio_path.download(output_path=file_dir, filename=file_name)
		
	# 동영상 다운로직
	else:
		# 선택한 quality 에 맞는 itag 를 구해옴
		for i, q in enumerate(video_quality): 
			if q + ".mp4" == quality:
				tag = video_itag[i]

		# download 하려면 변수에 stream 이 있어야 된다
		video_path = video.streams.get_by_itag(tag)
		audio_path = video.streams.get_audio_only()

        

		video_path = video_path.download(output_path=file_dir, filename=file_name.replace('.mp4', '')+"_video.mp4")
		audio_path = audio_path.download(output_path=file_dir, filename=file_name.replace('.mp4', '')+"_audio.mp3")

		# stream을 클립으로 저장
		videoclip = VideoFileClip(video_path) 
		audioclip = AudioFileClip(audio_path)

		videoclip.audio = audioclip
		
		videoclip.write_videofile(file_name)
		videoclip.close()
		audioclip.close()
	
		
		
		os.remove(video_path)
		os.remove(audio_path)
		
		# 망할 이 한줄때문에 삽질 5일함.. 연속으로 같은 파일 다운받으면 오류나서
		# video_path 개체를 제거해줘야 함
		del video_path
		del audio_path

	
	return render_template('loading.html', video_info=video_info)
	
def save(mp3_flag):
	# tk(), mainloop() tk 기본 틀
	file = Tk()

	# tk 기본창 숨김, 경로 선택창 최상위로
	
	file.withdraw()
	file.wm_attributes("-topmost", 1)
	file.focus()
	# ESC 누르면 먹통되는것 방지
	
	
	# mp3 검사
	if mp3_flag:
		
		file.dir = filedialog.asksaveasfilename(initialfile = video.title.replace('/','')+'.mp3', title="Save As", filetypes=[("MPEG3 files", "*.mp3"),("all files", "*")])
			
		
		# 파일명에 mp3가 없고 취소가 안 됐으면 확장자를 붙임
		if ".mp3" not in file.dir and file.dir != '':
			file.dir = file.dir + ".mp3"
		

	else:
		try:
			file.dir = filedialog.asksaveasfilename(initialfile	= video.title.replace('/', '')+'.mp4', title="Save As", filetypes=[("MPEG4 files", "*.mp4"),("all files", "*")])
			
		except Exception:
			return render_template('cancel.html', video_info=video_info)
		if ".mp4" not in file.dir and file.dir != '':
			file.dir = file.dir + ".mp4"



	file.destroy()
	file.mainloop()

	return file.dir


if __name__ == "__main__":
	app.run(host='0.0.0.0:5000')
	
	