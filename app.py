from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            response = requests.get(flipkart_url)
            flipkart_html = bs(response.text, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "tUxRFH"})
            del bigboxes[0:3]
            if not bigboxes:
                print("No products found on Flipkart for:", searchString)
                return "No products found. Please try a different search."
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding ='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "col EPCmJX"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    # name.encode(encoding='utf-8')
                    name = commentbox.find_all('div', {'class': 'row gHqwa8'})[0].div.p.text
                except:
                    name = 'No Name'

                try:
                    # rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    # commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.find_all('div', {'class': 'ZmyHeo'})
                    # custComment.encode(encoding='utf-8')
                    custComment = comtag[0].text
                    custComment = custComment = custComment.replace("READ MORE", "")
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
	
