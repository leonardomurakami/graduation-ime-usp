#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long

int previous_smaller(vector<int> arr, int ind){
    for(int i=(ind-1); i>0; i--) if (arr[i] < arr[ind]) return i;
    return 0
}

int next_smaller(vector<int> arr, int ind){
    for(int i=(ind+1); i<arr.size(); i++) if (arr[i] < arr[ind]) return i
    return 0
}

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);

    
}