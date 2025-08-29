# dc2s

시나리오 json 데이터는 다음과 같이 구성돼:
- metadata:
--title
--watermark
--chatters(이 부분은 데이터의 중복을 방지하기 위함):
---username1:
----name:username1
----avatar:{url_image}
---username2:
...
//예시 코드. 대화 내역이랑 형식이 거의 비슷하지? 거기에서 추가해서 sound(string, url이 들어갈 예정),meme(string),animation(string)
-contents:[
    {
        name:username1
        content:"메시지 내용"
        timestamp
        attachments
        sound
        meme
        animation
        
    }
        {
        name:username2
        content:"메시지 내용"
        timestamp
        attachments
        sound
        meme
        animation
        
    }
        {
        name:username1
        content:"메시지 내용"
        timestamp
        attachments
        sound
        meme
        animation
        
    }
    ...
]