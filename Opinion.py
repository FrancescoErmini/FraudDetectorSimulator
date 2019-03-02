class Opinion:
	
	b=0
	d=0
	u=1.0
	a=0

	def __init__(self, b, d, u, a):
		super(Opinion, self).__init__()
		self.b=b
		self.d=d
		self.u=u
		self.a=a

	def edit(self, pos,neg):
		self.b=(pos / (pos+neg+2.0))
		self.d=(neg / (pos+neg+2.0))
		self.u=(1.0 - self.b - self.d)

	def expectedValue(self):
		return (self.b + (self.a * self.u))

	def discount(self, that):
		belief = self.b *that.b
		disbelief = self.b * that.b
		uncertainty = (1.0 - belief - disbelief)
		alfa = self.a
		return Opinion(belief,disbelief,uncertainty,alfa)

	def consensus(self, that):
		if self.u == 0.0 and that.u == 0.0:
			belief = (self.b + that.b) / 2.0
			disbelief = (1.0 - self.belief)
			#disbelief = (self.d + that.d) / 2.0;
			uncertainty = 0.0
		else:
			denom = ((self.u + that.u) - (self.u * that.u));
			belief = (((self.b * that.u) + (self.b * this.u)) / denom);
			disbelief = (((self.d * that.u) + (self.d * this.u)) / denom);
			uncertainty = (1.0 - belief - disbelief);
			#uncertainty = ((this.u * that.u) / denom);
		#Math differs based on uncertainty values
		alpha = self.a;
		return Opinion(belief, disbelief, uncertainty, alpha)




