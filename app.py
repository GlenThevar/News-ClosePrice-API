from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)
swagger = Swagger(app)
        
class MarketNews(Resource):
    def get(self):
        """
        Get top market news.
        ---
        tags:
        - Market News
        responses:
            200:
                description: A list of top market news.
                content:
                    application/json:
                      schema:
                        type: array
                        items:
                            type: object
                            properties:
                                url:
                                    type: string
                                text:
                                    type: string
                                img_url:
                                    type: string
            500:
                description: Internal Server Error. Issue with retrieving market news.
        """
        url = 'https://www.livemint.com/market/stock-market-news'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        headline_elements = soup.find_all(class_='headline')
        img_sec_elements = soup.find_all(class_='imgSec')
        data = []
        for headline_element, img_sec_element in zip(headline_elements, img_sec_elements):
            anchor_element = headline_element.find('a')
            text = anchor_element.get_text().strip()
            url = urljoin(response.url, anchor_element.get('href'))
            img_element = img_sec_element.find('img')
            img_url = urljoin(response.url, img_element.get('src'))
            item = {'text': text, 'url': url, 'img_url': img_url}
            data.append(item)
        
        return jsonify(data)

class ClosePrices(Resource):
    def get(self):
        """
        This method responds to the GET request for retrieving close prices of a stock.
        ---
        tags:
        - Close Prices
        parameters:
            - name: ticker
              in: query
              type: string
              required: true
              description: The stock symbol (ticker) for which close prices are requested.
        responses:
            200:
                description: A successful GET request
                content:
                    application/json:
                      schema:
                        type: object
                        properties:
                            close_prices:
                                type: object
                                description: Close prices for the specified stock
            400:
                description: Bad Request. Invalid or not found stock symbol.
            500:
                description: Internal Server Error. Issue with retrieving close prices.
        """
        ticker_symbol = request.args.get('ticker')

        if not ticker_symbol:
            return jsonify({"error": "Stock symbol (ticker) is required"}), 400

        try:

            stock = yf.Ticker(ticker_symbol)


            if stock is None:
                return jsonify({"error": f"Invalid or not found stock symbol: {ticker_symbol}"}), 400

            hist = stock.history(period='6mo')


            close_prices = {date.strftime('%Y-%m-%d'): close for date, close in zip(hist.index, hist['Close'])}

            return jsonify({"close_prices": close_prices})

        except Exception as e:

            error_message = f"Internal Server Error. {str(e)}"
            return jsonify({"message": error_message}), 500
        

api.add_resource(MarketNews, "/market-news")
api.add_resource(ClosePrices, "/close-prices")

if __name__ == "__main__":
    app.run(debug=True)
