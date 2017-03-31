#include <bits/stdc++.h>
using namespace std;

vector <string> split(string s) {
	stringstream S(s);
	vector <string> res;
	string t;
	while(S >> t) { 
		if(t.find("Count") != string::npos || t.find("TagName") != string::npos)
			res.push_back(t);
	}
	return res;
}

int toInt(const string &s){ 
	stringstream ss; 
	ss << s; 
	int x; 
	ss >> x; 
	return x; 
}

string getTag(string &s) {
	int n = s.length();
	return s.substr(9, n - 10);
}

int getCount(string &s) {
	int n = s.length();
	return toInt(s.substr(7, n - 8));
}

pair <int, string> parse(vector <string> v) {
	string s = getTag(v[0]);
	int cnt = getCount(v[1]);
	return {cnt, s};
}


int main() {
	
	string s;
	vector <pair <int, string> > p;

	while(getline(cin, s)) {
		vector <string> temp;
		temp = split(s);
		if(!temp.empty()) { 
			p.push_back(parse(temp));
		}
	}   
	
	sort(p.rbegin(), p.rend());

	for(auto it: p) {
		cout << it.second << endl;
	}

	return 0;
}
