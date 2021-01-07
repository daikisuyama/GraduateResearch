import wave
import numpy as np
import os
import sys
import argparse
#CUI環境でのmatplotlibによる画像の保存
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import audioop
import pydub
from collections import OrderedDict

#条件:量子化ビットは2に統一しないとだめ
#条件:paramsのchannnel数は1

'''
ファイルの名前はパスで拡張子まで含めて指定
type:= 入力が"wav"か"ndarray"か
indata:= ファイル(.wavか.mp3)かndarray
params:= (入力がndarrayの時)paramsをtuple,OrderedDictのどちらかで指定
numtype:= (入力がwavの時)ndarrayへの変換のタイプ
'''

#paramsは全て固定にした方が良いか
#(1,2,44100,44100,"NONE","not compressed")
class AudioProcessing:
    def __init__(self,intype,indata,numtype="int16",params=None):
        #読み込み+初期化
        if intype=="wav":
            self.params=None
            self.data=None
            #ndarrayの型をここで決める
            if os.path.splitext(indata)[1]==".wav":
                self.load_conv_to_monaural(indata,numtype)
            elif os.path.splitext(indata)[1]==".mp3":
                #mp3の場合は変換
                sound=pydub.AudioSegment.from_mp3(indata)
                sound.export(os.path.splitext(indata)[0]+".wav",format="wav")
                self.load_conv_to_monaural(indata,numtype)
            else:
                print("Error: input extension must be wav or mp3",file=sys.stderr)
                exit()
        elif intype=="ndarray":
            if params is None:
                print("Error: params is necessary variable",file=sys.stderr)
                exit()
            else:
                self.params=params
                self.data=indata
        else:
            print("Error: invalid input type",file=sys.stderr)
            exit()

    #モノラルとして読み込んでndarrayに変換
    def load_conv_to_monaural(self,infile,numtype="int16"):
        #ファイルの読み込み
        inwav=wave.open(infile,mode="rb")
        #パラメータ,OrderedDictで変更可能に
        self.params=OrderedDict(inwav.getparams()._asdict())
        #byteオブジェクトで読み込み
        self.data=inwav.readframes(self.params["nframes"])
        inwav.close()
        #ステレオの場合はモノラルに変換
        if self.params["nchannels"]==2:
            #fragment??
            self.params["nchannels"]=1
            self.data=audioop.ratecv(self.data,self.params["sampwidth"],self.params["nchannels"],self.params["framerate"],self.params["framerate"],None)
            lsample=audioop.tomono(self.data[0],self.params["sampwidth"],1,0)
            rsample=audioop.tomono(self.data[0],self.params["sampwidth"],0,1)
            self.data=audioop.add(lsample,rsample,self.params["sampwidth"])
        #ndarrayへの読み込み
        self.data=np.frombuffer(self.data,dtype="int16")
        self.data=np.array(self.data,dtype=numtype)

    #4800000を超えるフレーム数の場合はplotできなくなる
    #ndarrayからwaveをplot,outdirに画像として保存
    #todo:細かい部分の表示できるように
    def plot_wav(self,outfile):
        #横軸は秒単位で(channel数かける)
        xaxis=np.arange(0,self.params["nframes"],1)
        #plot
        plt.plot(xaxis,self.data)
        #保存
        plt.savefig(outfile)

if __name__ == "__main__":
    infile=""
    outfile=""
    ap=AudioProcessing("wav",infile)
    ap.plot_wav(outfile)