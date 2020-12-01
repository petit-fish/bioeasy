import re
from datetime import datetime
import matplotlib
import requests
from bs4 import BeautifulSoup
from flask import Flask
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('averaged_perceptron_tagger')
import csv
import pandas as pd
import pandas

import bs4
import requests
import spacy
from spacy import displacy
import en_core_web_sm

nlp = en_core_web_sm.load()
from spacy.matcher import Matcher
from spacy.tokens import Span
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm

pd.set_option('display.max_colwidth', 200)
from matplotlib import pyplot as plt_final

# %matplotlib inline


nltk.download('punkt')

app = Flask(__name__)
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Post, Comment, Memo, Image
from operator import itemgetter

global reader
reader = ''
global e_link
e_link = 'a'


def home(request):
    return render(request, 'home.html', {})


def second(request):
    global userTextInput
    global totalLen
    global zipped_list

    request.encoding = 'utf-8'
    userTextInput = request.GET['userTextInput']
    linktogo(userTextInput)
    totalLen = len(titles)
    zipped_list = zip(pubid, titles, au_infos_final)
    return render(request, 'second.html',
                  {'userTextInput': userTextInput, 'totalLen': totalLen, 'zipped_list': zipped_list})


def linktogo(lala):
    crawlinglink = requests.get('https://www.ncbi.nlm.nih.gov/pmc/?term=' + lala)  # n-s
    raw = crawlinglink.text
    html = BeautifulSoup(raw, 'html.parser')

    global titles  # 제목
    titles_o = html.select('div.title a')
    titles = []
    for title in titles_o:
        title = remove_tag(str(title))
        titles.append(title)

    global pubid  # 논문id
    pub_id = html.select('dl.rprtid dd')
    pubid = []
    for pub in pub_id:
        pub = remove_tag(str(pub))
        pubid.append(pub)

    global au_infos_final  # 작가
    a_infos = html.select('div.supp')
    au_infos = []
    for i in a_infos:
        au_infos.append(remove_tag(str(i)))
    au_infos_final = []
    for i in range(0, len(au_infos)):
        au_infos_final.append((au_infos[i].split(','))[0:-1])
        au_infos_final[i] = au_infos_final[i][0:int(len(au_infos_final[i]) * 0.05) + 1]


def remove_tag(content):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', content)
    return cleantext


def third(request):
    global data
    data = request.GET['theid']
    readerLink = 'https://www.ncbi.nlm.nih.gov/pmc/articles/' + str(data) + '/?report=reader'
    posts = Post.objects.all().filter(base_id=data)
    memos = Memo.objects.all().filter(pmc_id=data)
    return render(request, 'third.html', {'link_toReader': readerLink, 'pmcID': data, 'posts': posts, 'memos': memos})

def keywordAbstract(request): # knowledge graph 탭 안의 'see knowledge graph' 텍스트가 클릭되면 실행되어야 할 부분입니다.
    data = request.GET['theid']  #data는 third 페이지에서 연 논문의 pmc id 입니다.(ex. pmc3373892)
    creating_CSV(data)             # data를 이용해 csv 파일을 만듭니다.
    keywordList = returning_keyword_list(str(data[3:])) #data에서 숫자부분만 parameter로 넣어서 keywordlist를 만듭니다.

    return render(request, 'graph.html', {'keywordList': keywordList, 'pmcID': data})

# keywordAbstract()에서 생성한 keywordList로 버튼을 만드시면 될 듯 합니다.
# 그 다음, 키워드 버튼이 하나라도 클릭되면 아래의 keywordToGraph()를 실행하게 하면 됩니다.


def keywordToGraph(request):
    data = request.GET['theid']
    creating_CSV(num=str(data))
    csv_to_graph(id_num=str(data[3:]))
    image_path = "image_file_{}".format(str(data[3:]))+".png"
    return render(request, 'show_graph.html', {'image_path': image_path})


def creating_CSV(num):
    headers = {'User-Agent': 'yumi'}
    url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/' + str(num) + '/'
    req = requests.get(url, headers=headers)
    raw = req.text
    html = BeautifulSoup(raw, 'html.parser')
    e_pubreader_html = html.get_text()
    final_full_text = only_main(remove_css(remove_tag(e_pubreader_html)))
    id = int(num[3:])  # PMC 아이디 값 넣기
    sentList = sent_tokenize(final_full_text)
    f = open('write{}.csv'.format(id), 'w', -1, 'utf-8', newline='')
    wr = csv.writer(f)
    wr.writerow(['sentence'])
    for i in sentList:
        wr.writerow([i])
    f.close()


def returning_keyword_list(id_num):
    candidate_sentences = pd.read_csv("write{}.csv".format(id_num))
    candidate_sentences.shape
    entity_pairs = []
    for i in tqdm(candidate_sentences['sentence']):
        entity_pairs.append(get_entities(i))
    relations = [get_relation(i) for i in tqdm(candidate_sentences['sentence'])]
    finalList=[]
    testlist = pd.Series(relations).value_counts().keys().tolist()
    for i in testlist:
        if (pd.Series(relations).value_counts()[i]>=5):  #빈도수 5이상 키워드만으로 리스트 구성
            finalList.append(i)
    testposlist = nltk.pos_tag(finalList)
    testFinalList = [word for word, pos in testposlist if pos in ['NNP', 'NNS','NNPS']]  #명사형 키워드들만 뽑기
    finalKeywordlist = testFinalList[:int(len(testFinalList)*1)] #빈도가 1이어도 그래프가 코랩에서 나오길래(?) 빈도수 상위 50%로 대략 구성하였습니다.
    return finalKeywordlist



def csv_to_graph(id_num):
    candidate_sentences = pd.read_csv("write{}.csv".format(id_num))
    candidate_sentences.shape
    entity_pairs = []
    for i in tqdm(candidate_sentences['sentence']):
        entity_pairs.append(get_entities(i))
    relations = [get_relation(i) for i in tqdm(candidate_sentences['sentence'])]
    # extract subject
    source = [i[0] for i in entity_pairs]
    # extract object
    target = [i[1] for i in entity_pairs]
    kg_df = pd.DataFrame({'source': source, 'target': target, 'edge': relations})
    # create a directed-graph from a dataframe
    G = nx.from_pandas_edgelist(kg_df, "source", "target",
                                edge_attr=True, create_using=nx.MultiDiGraph())
    plt.figure(figsize=(60, 50))
    pos = nx.spring_layout(G, k=0.5)  # k regulates the distance between nodes
    nx.draw(G, with_labels=True, node_color='orange', font_size='28', node_size=10000, node_shape='d',
            edge_cmap=plt.cm.Blues, pos=pos)
    # plt.show()
    plt_final.savefig("static/img/image_file_{}".format(id_num))


class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'


def add(request):
    data = request.GET['theid']
    crawlinglink = requests.get('https://www.ncbi.nlm.nih.gov/pmc/?term=' + data)
    raw = crawlinglink.text
    html = BeautifulSoup(raw, 'html.parser')
    thetitle = html.select('div.title a')
    title = remove_tag(str(thetitle))
    return render(request, 'add_post.html', {'base_id': data, 'base_title': title})


def add_memo(request):
    return render(request, 'add_memo.html')


def create_memo(request):
    if request.method == 'POST':
        memo = Memo()
        memo.body = request.POST['body']
        memo.name = request.user
        memo.pmc_id = request.POST['pmc_id']
        memo.save()
        message = 'created successful'
        return HttpResponse(message)


def create(request):
    if request.method == 'POST':
        post = Post()
        post.title = request.POST['title']
        post.body = request.POST['body']
        post.author = request.user
        post.base_id = request.POST['base_id']
        post.base_title = request.POST['base_title']
        post.publish = datetime.now()
        post.save()
        return redirect('post_detail', str(post.pk))


def createcomment(request, pk):
    if request.method == 'POST':
        comment = Comment()
        comment.post = get_object_or_404(Post, pk=pk)
        comment.body = request.POST['body']
        comment.name = request.user
        comment.date_added = datetime.now()
        comment.save()
        return redirect('post_detail', str(pk))
    return render(request, 'add_comment.html', {'pk': pk})





def update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.title = request.POST['title']
        post.body = request.POST['body']
        post.author = request.user
        post.base_id = request.POST['base_id']
        post.base_title = request.POST['base_title']
        post.publish = datetime.now()
        post.save()
        return redirect('post_detail', str(post.pk))
    return render(request, 'update_post.html', {'post': post})


def updatecomment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST':
        comment.post.pk = request.POST['post']
        comment.body = request.POST['body']
        comment.name = request.user
        comment.date_added = datetime.now()
        comment.save()
        return redirect('post_detail', str(comment.post.pk))
    return render(request, 'update_comment.html', {'comment': comment})


def delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        Post.objects.filter(id=pk).delete()
        return redirect('post_list')
    return render(request, 'delete_post.html', {'post': post})


def deletecomment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == "POST":
        Comment.objects.filter(id=pk).delete()
        return redirect('post_detail', str(comment.post.pk))
    return render(request, 'delete_comment.html', {'comment': comment})


def delete_memo(request, pk):
    memo = get_object_or_404(Memo, pk=pk)
    if request.method == "POST":
        url = Memo.objects.values_list('pmc_id', flat=True).get(id=pk)
        Memo.objects.filter(id=pk).delete()
        return redirect('/third?theid='+str(url))
    return render(request, 'delete_memo.html', {'memo': memo})


def remove_tag(content):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', content)
    return cleantext


def remove_css(content):
    cleanr = re.compile('{.*}')
    cleantext = re.sub(cleanr, '', content)
    cleanr = re.compile('\n|\t')
    cleantext = re.sub(cleanr, '', cleantext)
    return cleantext


def only_main(content):
    start = content.find('Abstract')
    cleantext = content[start:]
    final = cleantext.find('Article information[\S]+')
    # print('information',final)
    cleantext = cleantext[:final]
    final = cleantext.find('References')
    # print('reference는',final)
    cleantext = cleantext[:final]
    return cleantext





def get_entities(sent):
    ## chunk 1
    ent1 = ""
    ent2 = ""

    prv_tok_dep = ""  # dependency tag of previous token in the sentence
    prv_tok_text = ""  # previous token in the sentence

    prefix = ""
    modifier = ""

    #############################################################

    for tok in nlp(sent):
        ## chunk 2
        # if token is a punctuation mark then move on to the next token
        if tok.dep_ != "punct":
            # check: token is a compound word or not
            if tok.dep_ == "compound":
                prefix = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == "compound":
                    prefix = prv_tok_text + " " + tok.text

            # check: token is a modifier or not
            if tok.dep_.endswith("mod") == True:
                modifier = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == "compound":
                    modifier = prv_tok_text + " " + tok.text

            ## chunk 3
            if tok.dep_.find("subj") == True:
                ent1 = modifier + " " + prefix + " " + tok.text
                prefix = ""
                modifier = ""
                prv_tok_dep = ""
                prv_tok_text = ""

                ## chunk 4
            if tok.dep_.find("obj") == True:
                ent2 = modifier + " " + prefix + " " + tok.text

            ## chunk 5
            # update variables
            prv_tok_dep = tok.dep_
            prv_tok_text = tok.text
    #############################################################

    return [ent1.strip(), ent2.strip()]


def get_relation(sent):
    doc = nlp(sent)

    # Matcher class object
    matcher = Matcher(nlp.vocab)

    # define the pattern
    pattern = [{'DEP': 'ROOT'},
               {'DEP': 'prep', 'OP': "?"},
               {'DEP': 'agent', 'OP': "?"},
               {'POS': 'ADJ', 'OP': "?"}]

    matcher.add("matching_1", None, pattern)

    matches = matcher(doc)
    k = len(matches) - 1

    span = doc[matches[k][1]:matches[k][2]]

    return (span.text)

