import unittest, datetime
from trading import *

class TestQuik:

    @classmethod
    def cmd2str(self,cmd):
        return ";".join( [ ("%s=%.2f" if name == "price" else "%s=%s") % ( name.upper(), cmd[name] ) for name in cmd ] )
    
    def execute(self,cmd,callback):
        self.last_cmd = TestQuik.cmd2str( cmd )


class TickerTest(unittest.TestCase):

    def setUp(self):
        self.quik = TestQuik()
        self.market = Market( self.quik )
        self.ticker = self.market.SBER
        self.ticker.classcode = "SBERCC"

    def testFactory(self):
        self.ticker.price = 1.0
        self.assertEquals(self.ticker.price, self.market.SBER.price)

    def testSeries(self):
        self.ticker.time = datetime.datetime.now()
        self.ticker.price = 10.0
        self.ticker.tick()
        self.assertEquals(self.ticker('time').data()[0], self.ticker.time )
        self.assertEquals(self.ticker('time').size, 1 )
        self.assertEquals(len(self.ticker('time').data()), 1 )
        self.assertEquals(self.ticker('price').data()[0], 10.0 )
        self.assertEquals(self.ticker('price').size, 1 )

    def testHistory(self):
        self.market.load("test/testdata-1000.txt")
        self.assertEquals(self.ticker('time').size, 1000)

    def testIndicator(self):
        ind = self.ticker("MA", Indicator)
        self.market.load("test/testdata-1000.txt")
        self.assertEquals(self.ticker('time').size, 1000)
        A = ind.data()
        del( self.ticker.series["MA"] )
        B = self.ticker("MA").data()
        for i in range( len(A) ): self.assertAlmostEqual( A[i], B[i] )


    def testOrderCreation(self):
        o1 = self.market.SBER.order( 100 )
        self.assertEquals( o1.order_key, 100 )
        o1.price = 555
        o2 = self.market.SBER.order( 100 )
        self.assertEquals( o2.price, 555 )

    def testOrderExecution(self):
        Order.LAST_ID=0
        order = self.market.SBER.buy(100,1)
        self.assertEquals( order.operation, BUY )
        self.assertEquals( order.price, 100 )
        self.assertEquals( order.quantity, 1 )
        order.submit()
        self.assertEquals( self.quik.last_cmd, "ACCOUNT=L01-00000F00;CLASSCODE=SBERCC;PRICE=100.00;CLIENT_CODE=52709;ACTION=NEW_ORDER;OPERATION=B;SECCODE=SBER;TRANS_ID=1;QUANTITY=1")
        order = self.market.SBER.sell(MARKET_PRICE,10)
        order.submit()
        self.assertEquals( self.quik.last_cmd, "ACCOUNT=L01-00000F00;CLASSCODE=SBERCC;PRICE=0.00;CLIENT_CODE=52709;ACTION=NEW_ORDER;OPERATION=S;SECCODE=SBER;TRANS_ID=2;QUANTITY=10" )
        order.order_key = "OK-%s" % order.trans_id
        order.kill()
        self.assertEquals( self.quik.last_cmd, "ACTION=KILL_ORDER;SECCODE=SBER;CLASSCODE=SBERCC;TRANS_ID=3;ORDER_KEY=OK-2" )

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TickerTest))
    unittest.TextTestRunner(verbosity=2).run(suite)
