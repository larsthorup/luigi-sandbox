import requests
import luigi
from luigi.format import UTF8
from bs4 import BeautifulSoup
from collections import Counter
import pickle
import datetime


class GlobalParams(luigi.Config):
    NumberBooks = luigi.IntParameter(default=10)
    NumberTopWords = luigi.IntParameter(default=500)


class GetTopBooks(luigi.Task):
    """
    Get list of the most popular books from Project Gutenberg
    """

    def output(self):
        return luigi.LocalTarget("data/books_list.txt")

    def run(self):
        resp = requests.get("http://www.gutenberg.org/browse/scores/top")

        # simulate busy work
        # start = datetime.datetime.now()
        # while (datetime.datetime.now() - start).seconds < 60 * 20:
        #     data = []
        #     for i in range(1000):
        #         data.append(i)

        soup = BeautifulSoup(resp.content, "html.parser")

        pageHeader = soup.find_all("h2", string="Top 100 EBooks yesterday")[0]
        listTop = pageHeader.find_next_sibling("ol")

        with self.output().open("w") as f:
            for result in listTop.select("li>a"):
                if "/ebooks/" in result["href"]:
                    f.write("http://www.gutenberg.org{link}.txt.utf-8\n"
                        .format(
                            link=result["href"]
                        )
                    )


class DownloadBooks(luigi.Task):
    """
    Download a specified list of books
    """
    FileID = luigi.IntParameter()

    REPLACE_LIST = """.,"';_[]:*-"""

    def requires(self):
        return GetTopBooks()

    def output(self):
        return luigi.LocalTarget("data/downloads/{}.txt".format(self.FileID), format=UTF8)

    def run(self):
        with self.input().open("r") as i:
            URL = i.read().splitlines()[self.FileID]

            with self.output().open("w") as outfile:
                book_downloads = requests.get(URL)
                book_text = book_downloads.text

                for char in self.REPLACE_LIST:
                    book_text = book_text.replace(char, " ")

                book_text = book_text.lower()
                outfile.write(book_text)


class CountWords(luigi.Task):
    """
    Count the frequency of the most common words from a file
    """

    FileID = luigi.IntParameter()

    def requires(self):
        return DownloadBooks(FileID=self.FileID)

    def output(self):
        return luigi.LocalTarget(
            "data/counts/count_{}.pickle".format(self.FileID),
            format=luigi.format.Nop
        )

    def run(self):
        with self.input().open("r") as i:
            word_count = Counter(i.read().split())

            with self.output().open("w") as outfile:
                pickle.dump(word_count, outfile)


class TopWords(luigi.Task):
    """
    Aggregate the count results from the different files
    """

    def requires(self):
        requiredInputs = []
        for i in range(GlobalParams().NumberBooks):
            requiredInputs.append(CountWords(FileID=i))
        return requiredInputs

    def output(self):
        return luigi.LocalTarget("data/summary.txt", format=UTF8)

    def run(self):
        total_count = Counter()
        for input in self.input():
            with input.open("rb") as infile:
                nextCounter = pickle.load(infile)
                total_count += nextCounter

        with self.output().open("w") as f:
            for item in total_count.most_common(GlobalParams().NumberTopWords):
                f.write("{0: <15}{1}\n".format(*item))
