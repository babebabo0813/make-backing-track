"""Measure alignment and prepare backing vocals without changing sources."""
import argparse, json, re, subprocess, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('original','instrumental','backing','ffmpeg','work-dir'):
        p.add_argument('--'+name,required=True)
    p.add_argument('--deps-dir')
    p.add_argument('--backing-db',type=float,default=-3)
    p.add_argument('--target-sample-peak-db',type=float,default=-1.5)
    a=p.parse_args()
    if a.deps_dir: sys.path.insert(0,a.deps_dir)
    import numpy as np
    work=Path(a.work_dir);work.mkdir(parents=True,exist_ok=True)
    output=work/'backing_aligned.wav'; report_path=work/'preparation.json'
    if output.exists() or report_path.exists():
        raise RuntimeError('Preparation outputs already exist; choose a new work directory.')
    def decode(path,rate,mono=False,start=None,duration=None):
        cmd=[a.ffmpeg,'-nostdin','-v','error']
        if start is not None:cmd+=['-ss',str(start)]
        cmd+=['-i',path]
        if duration is not None:cmd+=['-t',str(duration)]
        cmd+=['-ar',str(rate),'-ac','1' if mono else '2','-f','f32le','pipe:1']
        data=np.frombuffer(subprocess.check_output(cmd),dtype='<f4')
        return data if mono else data.reshape(-1,2)
    def correlate(x,y,rate,center=0,radius=None):
        x=x.astype(float);y=y.astype(float);n=min(len(x),len(y));x=x[:n];y=y[:n]
        x-=x.mean();y-=y.mean()
        denom=np.sqrt(np.dot(x,x)*np.dot(y,y))
        if denom<1e-12:raise RuntimeError('Selected alignment window is silent.')
        fftn=1<<(2*n-1).bit_length()
        c=np.fft.irfft(np.fft.rfft(x,fftn)*np.conj(np.fft.rfft(y,fftn)),fftn)
        r=rate if radius is None else radius
        lags=np.arange(center-r,center+r+1)
        v=c[lags%fftn]/denom;idx=int(np.argmax(v))
        return int(lags[idx]),float(v[idx])
    info=subprocess.run([a.ffmpeg,'-hide_banner','-i',a.instrumental],capture_output=True,text=True,encoding='utf-8',errors='replace').stderr
    match=re.search(r'Audio:.*?([0-9]+) Hz',info)
    if not match:raise RuntimeError('Could not identify instrumental sample rate.')
    rate=int(match[1])
    orig8=decode(a.original,8000,True);inst8=decode(a.instrumental,8000,True)
    duration=min(len(orig8),len(inst8))/8000
    if duration<3:raise RuntimeError('Audio too short for reliable automatic alignment.')
    width=min(8,duration/3)
    times=np.linspace(min(8,duration/10),max(min(8,duration/10),duration-width-1),5)
    windows=[]
    for t in times:
        i=int(t*8000);n=int(width*8000)
        delay,corr=correlate(orig8[i:i+n],inst8[i:i+n],8000)
        windows.append({'at':float(t),'lag':delay/8000,'correlation':corr})
    reliable=[w for w in windows if w['correlation']>=0.35]
    if len(reliable)<3 or np.ptp([w['lag'] for w in reliable])>0.003:
        raise RuntimeError('Weak or inconsistent alignment; inspect versions and speed before mixing. '+json.dumps(windows))
    center=round(float(np.median([w['lag'] for w in reliable]))*rate)
    fine=[]
    for w in reliable:
        x=decode(a.original,rate,True,w['at'],width)
        y=decode(a.instrumental,rate,True,w['at'],width)
        d,c=correlate(x,y,rate,center,max(8,round(rate*.0005)))
        fine.append(d)
    delay=round(float(np.median(fine)))
    inst=decode(a.instrumental,rate);bv=decode(a.backing,rate)
    if abs(len(bv)/rate-len(orig8)/8000)>1:
        raise RuntimeError('Backing length differs from original; establish its time origin manually.')
    aligned=np.zeros_like(inst)
    src=max(0,delay);dst=max(0,-delay);n=min(len(bv)-src,len(inst)-dst)
    if n<=0:raise RuntimeError('No overlapping audio after alignment.')
    aligned[dst:dst+n]=bv[src:src+n]
    fade=min(round(rate*.005),n//2)
    if fade:
        aligned[dst:dst+fade]*=np.linspace(0,1,fade,dtype=np.float32)[:,None]
        aligned[dst+n-fade:dst+n]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
    cmd=[a.ffmpeg,'-nostdin','-v','error','-f','f32le','-ar',str(rate),'-ac','2','-i','pipe:0','-c:a','pcm_f32le',str(output)]
    subprocess.run(cmd,input=aligned.astype('<f4').tobytes(),check=True)
    mix=inst+aligned*10**(a.backing_db/20)
    peak=float(np.max(np.abs(mix)))
    raw_peak_db=float(20*np.log10(max(peak,1e-12)))
    master_db=min(0,a.target_sample_peak_db-raw_peak_db)
    report={'sample_rate':rate,'duration':len(inst)/rate,'original_lag_samples':delay,'original_lag_seconds':delay/rate,'alignment_windows':windows,'aligned_backing':str(output.resolve()),'backing_relative_db':a.backing_db,'suggested_instrumental_gain_db':master_db,'suggested_backing_gain_db':master_db+a.backing_db,'note':'These are sample-peak estimates. Check true peak after Audacity export and reduce both track gains if needed.'}
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
