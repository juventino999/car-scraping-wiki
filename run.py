import spiders.Buddy as spider

spider.process.crawl(spider.Buddy)
spider.process.start()

import matplotlib.pyplot as plt
from data.analysis import plot, cars


plt.show()
print(cars.to_string())
