
# -*- coding: utf-8 -*-

'''
@Description:
网易云音乐评论爬虫，可以完整爬取整个评论
部分参考了@平胸小仙女的文章(地址:https://www.zhihu.com/question/36081767)
post加密部分也给出了，可以参考原帖：
作者：平胸小仙女
链接：https://www.zhihu.com/question/36081767/answer/140287795
来源：知乎
'''

import BaseData
import json
import sql
import threading
import pymysql




# 抓取某一首歌的热门评论
def get_hot_comments(song_id):
    url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_" + str(song_id) + "/?csrf_token="
    json_text = BaseData.get_commentsjson(url,1)
    #容错
    if (json_text):
        json_dict = json.loads(json_text)
        hot_comments = json_dict['hotComments']  # 热门评论数组
        commentscount = len(hot_comments)
        print("共有%d条热门评论!" % commentscount)

        for index, item in enumerate(hot_comments):
            commentId = item['commentId'] #评论id
            comment = item['content']  # 评论内容
            likedCount = item['likedCount']  # 点赞总数
            comment_time = item['time']  # 评论时间(时间戳)
            userID = item['user']['userId']  # 评论者id
            nickname = item['user']['nickname']  # 评论者昵称
            avatarUrl = item['user']['avatarUrl']  # 评论者头像地址
            print ('歌曲id:%s 评论用户:%s 评论内容:%s 点赞总数:%s' %(song_id,nickname,comment,likedCount))

            try:
                # 将热门评论数据保存到数据库中
                sql.save_hotcomments_by_a_song(song_id, userID, nickname, avatarUrl, comment_time, likedCount, comment,
                                               commentId)
                num = index + 1
                print ("保存热门评论的进度:%d / %d" % (num, commentscount))
            except:
                print ('该条评论存入数据库失败')
            else:
                continue


    else:
        print('歌曲id为:%s的歌曲热门评论加载失败,该歌曲热门评论不会写入到数据库中' %(song_id))




# 抓取某一首歌的全部评论
def get_all_comments(song_id,ifmaxpage,maxpage):
    url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_" + str(song_id) + "/?csrf_token="
    #获取首页Json数据，根据total字段拿到全部的评论数
    json_text = BaseData.get_commentsjson(url,1)

    #容错
    if (json_text):
        json_dict = json.loads(json_text)
        comments_num = int(json_dict['total'])
        # 每页返回20条评论数据
        if (comments_num % 20 == 0):
            totalpage = comments_num / 20
        else:
            totalpage = int(comments_num / 20) + 1

        # 判断是否控制抓取的最大页数
        if (ifmaxpage):
            print("共有%d条评论,合计%d页,此次抓取仅抓取前%d页!" % (comments_num, totalpage, maxpage))
            totalpage = maxpage
        else:
            print("共有%d条评论,合计%d页,此次抓取为全部数据的抓取!" % (comments_num, totalpage))

        for page in range(1,totalpage+1):  # 逐页抓取

            json_text = BaseData.get_commentsjson(url, page)
            #容错
            if (json_text):

                json_dict = json.loads(json_text)  # 获取到该页相应的评论数组数据
                normal_comments = json_dict['comments']  # 普通评论数组

                for index,item in enumerate(normal_comments):
                    commentId = item['commentId']  # 评论id
                    comment = item['content']  # 评论内容
                    likedCount = item['likedCount']  # 点赞总数
                    comment_time = item['time']  # 评论时间(时间戳)
                    userID = item['user']['userId']  # 评论者id
                    nickname = item['user']['nickname']  # 评论者昵称
                    avatarUrl = item['user']['avatarUrl']  # 评论者头像地址

                    print ('歌曲id:%s 评论用户:%s 评论内容:%s 点赞总数:%s' % (song_id, nickname, comment, likedCount))

                    try:
                        # 将热门评论数据保存到数据库中
                        sql.save_normalcomments_by_a_song(song_id, userID, nickname, avatarUrl, comment_time, likedCount,comment,commentId)
                        num = index + 1
                        print ("保存该页普通评论的进度:%d / %d" % (num, len(normal_comments)))
                    except:
                        print ('该条评论存入数据库失败')
                    else:
                        continue


                print("第%d页写入完毕! 共%d页" % (page, totalpage))
            else:
                print('歌曲id为%s的歌曲第%d页评论获取失败' %(song_id,page))




if __name__ == "__main__":
    music_id = input("请输入你要抓取的歌曲id(例如<晴天>的id为: 186016 <温柔(live)>的id为: 28167426)")
    savetype = input("抓取热门评论请输入1,抓取普通评论请输入2")


    if int(savetype) == 1:
        #抓取热门评论

        # 开辟一个线程
        t0 = threading.Thread(target=get_hot_comments, args=(music_id,))
        t0.start()
    else:
        #抓取普通评论
        iflimit =  input('全部数量较多，是否限制抓取页数？ 1是 0否')
        if (int(iflimit) == 1):
            #限制页数:
            maxpage = input('亲,每首歌抓取多少页的评论呢?直接输入数字即可')
            print('开始抓取前%d页评论' % int(maxpage))
            t1 = threading.Thread(target=get_all_comments, args=(music_id,True,maxpage,))
            t1.start()
        else:
            #不限制页数:
            maxpage = 0
            print('开始抓取歌曲全部评论')
            t1 = threading.Thread(target=get_all_comments, args=(music_id,False,maxpage,))
            t1.start()
























