# usage: python3 solve_race.py frags.json NVARS SECONDS OUT
# Races MapleChrono + MapleCM (plain + shuffled copies); writes a verified assignment to OUT.
import json,sys,time,random,multiprocessing as mp
F,N,T,OUT=sys.argv[1],int(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
d=json.load(open(F)); cl=[c for k in sorted(d,key=int) for c in d[k]]
def verify(a): return all(any((l>0)==(a[abs(l)-1]=='1') for l in c) for c in cl)
def worker(q,name,seed):
    from pysat.solvers import Solver
    c=[list(x) for x in cl]
    perm=list(range(1,N+1))
    if seed:
        r=random.Random(seed); r.shuffle(c); r.shuffle(perm)
        for x in c: r.shuffle(x)
    mp_=dict(zip(range(1,N+1),perm)); inv={v:k for k,v in mp_.items()}
    c=[[mp_[abs(l)]*(1 if l>0 else -1) for l in x] for x in c]
    s=Solver(name=name,bootstrap_with=c)
    if s.solve():
        a=['0']*N
        for v in s.get_model():
            if 0<abs(v)<=N and v>0: a[inv[v]-1]='1'
        q.put((name,seed,''.join(a)))
if __name__=='__main__':
    import os
    jobs=[tuple((x.split(':')[0],int(x.split(':')[1]))) for x in os.environ.get('JOBS','maplechrono:0,maplecm:0,maplechrono:11,maplecm:23').split(',')]
    q=mp.Queue(); ps=[mp.Process(target=worker,args=(q,n,s),daemon=True) for n,s in jobs]
    t=time.time()
    for p in ps: p.start()
    res=None
    while time.time()-t<T:
        try: n,s,a=q.get(timeout=2)
        except Exception: continue
        if len(a)==N and verify(a): res=a; print('winner',n,s,flush=True); break
    for p in ps: p.terminate()
    if res: open(OUT,'w').write(res); print('SOLVED',round(time.time()-t,1))
    else: print('UNSOLVED',round(time.time()-t,1))
