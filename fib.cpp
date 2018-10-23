#include<iostream>
#include<vector>
#include<string>
class Str_Computer
{
private:
	std::vector<char> numbers;
	const std::vector<char> & Number()const
	{
		return numbers;
	} 
public:
	Str_Computer(int n =0)
	{
		int i;
		while(n>0)
		{
			i = n%10;
			numbers.insert(numbers.begin(),i+48);
			n/=10;
		}
	}
	int size()const
	{
		return numbers.size();
	}
	//reload add
	const Str_Computer & operator+(Str_Computer &v)
	{
		int op_add = 0;
		int min = this->size();
		bool flag = true;
		if(min>v.size())
		{
			min = v.size();
			flag =false;
		}
		std::vector<char> temp;
		int x1;
		int x2;
		for(int i =0;i<min;i++)
		{
			x1 = this->numbers.back() -48;
			x2 = v.numbers.back()-48;
			std::cout<<x1<<' '<<x2<<std::endl;
			this->numbers.pop_back();
			v.numbers.pop_back();
			x1+=x2;
			x1+=op_add;
			if(x1/10)
			{
				op_add =1;
			} 
			else
			{
				op_add =0;
			}

			temp.insert(temp.begin(),(x1%10)+48);
		}
		if(!flag)
		{
			for(int i =0;i<this->size();i++)
			{
				x1 = this->numbers.back()-48;
				this->numbers.pop_back();
				x1+=op_add;
				if(x1/10)
				{
					op_add =1;
				} 
				else
				{
					op_add =0;
				}
				temp.insert(temp.begin(),(x1%10)+48);
			}
		}
		else
		{
			for(int i =0;i<v.size();i++)
			{
				x1 = this->numbers.back()-48;
				this->numbers.pop_back();
				x1+=op_add;
				if(x1/10)
				{
					op_add =1;
				} 
				else
				{
					op_add = 0;
				}
				temp.insert(temp.begin(),(x1%10)+48);

			}
		}
		if(1 == op_add)
		{
			temp.insert(temp.begin(),op_add+48);
		}
		this->numbers=temp;
		return *this;
	}
	friend std::ostream& operator<<(std::ostream & out,const Str_Computer & st)
	{
		for(std::vector<char>::const_iterator it = st.Number().begin();it<st.Number().end();it++)
		{
			out<<*it;
		}
		return out;
	}
};

int main(int argc, char const *argv[])
{

	Str_Computer s = Str_Computer(1839);
	Str_Computer s1 = Str_Computer(220);
	s+s1;
	std::cout<<s;
	return 0;
}