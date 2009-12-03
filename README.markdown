LPad
====

A light music player for Linux.

CopyRight (C) 2008 Chen Zheng <nkchenz@gmail.com> 
Distributed under terms of GPL v2

http://code.google.com/p/lpad/

Features
--------
* support ape, flac cue files
* play rar files directly without extracting, be nice to p2p software like emule
* drag and drop
* playlist support
* support lyric show
* lyric auto search by baidu.com or google.com
* 更好中文支持

依赖
----

    python, python-gtk2, mplayer, gstreamer0.10-plugins-ugly

Optional: mp3info unrar

apt-get 用户可使用下列命令安装依赖关系

    sudo apt-get install python python-gtk2 mplayer gstreamer0.10-plugins-ugly mp3info unrar

运行
----

    python lpad.py

已知问题
--------

mplayer的播放对有的歌曲长度信息识别有误，暂不影响播放

发现有的cue文件定位不准，但是在win下一切正常，经测量可以听到音乐的时间，也就是
实际播放时间real_t，和win差不多是一样的。只是显示时间display_t的问题。假设cue
中的偏移量正确，从win正常可以得出，那么如果mplayer的seek工作正常，经过real_t后，
音乐应该停止。但实际上并没有停止，音乐滞后，可以得出seek工作并不正常，seek后的
位置小于给定的位置。初步猜测可能和音乐文件的编码比特率有关系

帮助
----

在播放列表中，可以使用d，D，Del键删除选定的歌曲.
使用s，S键快速保存默认播放列表。

