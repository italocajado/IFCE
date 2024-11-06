class ThreadCpuBound extends Threads{
	
	public ThreadCpuBound (String nome) {
		super(nome);
	}
	
	public void run() {
		long contInt= 0;
		while(true) {
			double soma = 0;
			for(int i=0; i<10000; i++)
				for(int j=0; j<2000; j++) {
					soma = soma + Math.sin(i) +Math.sin(j);
				}
			contInt++;
			System.out.println(getName()+": "+contInt+"Interações");
		}
	}
	
	public static class myThread{
		public static void main(String[] args) {
			ThreadCpuBound t1 = new ThreadCpuBound("T1");
			ThreadCpuBound t2 = new ThreadCpuBound("T2");
			t1.setPriority(3);
			t2.setPriority(2);
			t1.start();
			t2.Start();

		}
	}
}