import random
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
from operator import attrgetter
import pandas as pd
from matplotlib import animation
import datetime

class Genetic:
    def __init__(self,n_gene,n_ind,CXPB,MUTPB,MUTINDPB,NGEN):
        self.n_gene = n_gene
        self.n_ind = n_ind
        self.CXPB = CXPB
        self.MUTPB = MUTPB
        self.MUTINDPB = MUTINDPB
        self.NGEN = NGEN

    def main(self):
        #ステップ1：初期世代の生成
        df = pd.DataFrame()
        pop = create_pop(n_ind, n_gene)
        set_fitness(evalOneMax, pop)
        
        df = pd.concat([df,opt_pop(pop)])
        df["世代"] = 0
        
        indx = []
        fitn = []
        val = []
        for i in pop:
            indx.append(i)
            fitn.append(min(i["fitness"]))
        df2 = pd.DataFrame({"indx":indx,"fitn":fitn})
        best_ind = min(pop[min(df2["fitn"].index)]["fitness"])
        print("Generation loop start!")
        print("Generation: 0 Best fitness: "+ str(best_ind))

        #世代を繰り返す
        for g in range(NGEN):
            #ステップ2：選択
            offspring = selTournament(pop,n_ind,t_size=3)
            #ステップ3：交叉
            crossover = []
            for child1,child2 in zip(offspring[::2],offspring[1::2]):
                if random.random() < CXPB:
                    
                    child1,child2 = cxTwoPointCopy(child1,child2)
                    child1["fitness"] = None
                    child2["fitness"] = None
                crossover.append(child1)
                crossover.append(child2)
            offspring = crossover[:]
            #ステップ4：突然変異
            mutant = []
            for mut in offspring:
                if random.random() <= MUTPB:
                    mut = mutFlipBit(mut, MUTINDPB)
                    mut["fitness"] = None
                mutant.append(mut)
            offspring = mutant[:]
            #次世代集団の生成
            pop = offspring[:]
            
            set_fitness(evalOneMax,pop)
            #最も適応度の高い個体の抽出
            indx = []
            fitn = []
            val = []
            for i in pop:
                indx.append(i)
                fitn.append(min(i["fitness"]))
            df2 = pd.DataFrame({"indx":indx,"fitn":fitn})
            best_ind = min(pop[min(df2["fitn"].index)]["fitness"])

            print("Generation: " + str(g+1) +" Best fitness: " + str(best_ind))
            df_hoge = opt_pop(pop)
            df_hoge[u"世代"] = g+1
            df = pd.concat([df,df_hoge])
        print("Generation loop ended! \n The best individual: ")
        print(best_ind)  
        
        #可視化
        c1 = c2 = np.arange(-10, 10, 0.1)
        xx, yy = np.meshgrid(c1, c2)

        len=np.size(c1)  
        zz=np.empty((len, len))

        for i in range(len):
            for j in range(len):
                xin=np.array([xx[i,j], yy[i,j]])
                zz[i,j] = bird(xin)

        fig = plt.figure(figsize=(12,12), dpi=80)
        ax = p3.Axes3D(fig)

        
        ax.set_xlim3d([10, -10])        
        ax.set_ylim3d([-10, 10])
        ax.set_xlabel('X')
        ax.set_xlabel('Y')
        
        def run(i):
            plt.cla()
            x,y,z,fit = [],[],[],[]
            ax.plot_wireframe(xx, yy, zz, alpha=1)
            x.append(df.where(df["世代"]==i).dropna()["x"])
            y.append(df.where(df["世代"]==i).dropna()["y"])
            z.append(df.where(df["世代"]==i).dropna()["result"])
            fit.append(df.where(df["世代"]==i).dropna()["result"].min())
            ax.scatter(x,y,z,alpha=1, s=50, c="r",label='Generation: {}, '.format(i)+"Best_fitness: {}".format(fit))
            plt.legend(loc='upper left', fontsize=24)

        ani = animation.FuncAnimation(fig, run,  blit=False, interval=500, frames = NGEN, repeat=True)
        now = datetime.datetime.now()
        ani.save("GA_{}.gif".format(now.strftime("%H_%M")),writer='imagemagick')

def opt_pop(pop):
    df = pd.DataFrame()
    for i in pop:
        df1 = pd.DataFrame(i[i["result"].idxmin():i["result"].idxmin()+1])
        df = pd.concat([df,df1],ignore_index=True).copy()
    df.pop("fitness")
    return df


def bird(x):
    x1 = x[0]
    x2 = x[1]
    t = np.sin(x1)*np.exp((1-np.cos(x2))**2)+np.cos(x2)*np.exp((1-np.sin(x1))**2)+(x1-x2)**2
    return t

class Individual(np.ndarray):
    #個体の格納
    fitness = None
    def __new__(cls, a):
        return np.asarray(a).view(cls)

def create_ind(n_gene):
    xli = []
    yli = []
    for i in range(n_gene):
        xli.append(random.uniform(-10,10))
        yli.append(random.uniform(-10,10))
    result = []
    for i,j in zip(xli,yli):
        result.append(bird([i,j]))
    df = pd.DataFrame({"x":xli,"y":yli,"result":result,"fitness":None})
    return df


def create_pop(n_ind, n_gene):
    pop = []
    for i in range(n_ind):
        ind = create_ind(n_gene)
        pop.append(ind)
    
    return pop

def set_fitness(eval_func,pop):
    for i,n in zip(range(n_ind), map(eval_func, pop)):
        pop[i]["fitness"] = n
    return pop

def evalOneMax(ind):
    return min(ind["result"])

def selTournament(pop,n_ind,t_size):
    chosen = []
    
    for i in range(n_ind):
        fit = []
        aspirant = [random.choice(pop) for j in range(t_size)]
        for n in range(t_size):
            fit.append(min(aspirant[n]["fitness"]))
        df1 = pd.DataFrame({"fit":fit})
        chosen.append(aspirant[df1["fit"].idxmin()])
    return chosen

def cxTwoPointCopy(ind1,ind2):
    size = len(ind1)
    tmp1 = ind1.copy()
    tmp2 = ind2.copy()

    cxPoint1 = random.randint(1,size)
    cxPoint2 = random.randint(1,size - 1)
    if cxPoint2 >= cxPoint1:
        cxPoint2 += 1
    else:
        cxPoint1,cxPoint2 = cxPoint2,cxPoint1
    tmp1[cxPoint1:cxPoint2],tmp2[cxPoint1:cxPoint2] = tmp2[cxPoint1:cxPoint2].copy(),tmp1[cxPoint1:cxPoint2].copy()
    
    return tmp1,tmp2

def mutFlipBit(ind,indpb):
    tmp = ind.copy()
    size = len(ind)
    for i in range(len(ind)):
        if random.random() <= indpb:
            x = random.uniform(-10,10)
            y = random.uniform(-10,10)
            hoge = [x,y]
            result = bird(hoge)
            fitness = result
            hoo = pd.DataFrame({"x":[x],"y":[y],"result":[result],"fitness":[fitness]})
            tmp[i:i+1] = hoo.values
    return tmp


if __name__ == "__main__":
    ''' n_gene = input("遺伝子の個数を入力してください")
    n_ind = input("世代内の個体の個数を入力してください")
    CXPB = input("交叉確率を入力したください")
    MUTPB = input("個体の突然変異確率を入力してください")
    MUTINDPB = input("世代の突然変異確率を入力してください")
    NGEN = input("世代の繰り返し回数を入力してください") '''
    n_gene = 50
    n_ind = 50
    CXPB = 0.5
    MUTPB = 0.4
    MUTINDPB = 0.1
    NGEN = 50

    run = Genetic(n_gene,n_ind,CXPB,MUTPB,MUTINDPB,NGEN)
    run.main()




