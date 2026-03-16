#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);
    
    int n, a;
    int pairs = 0;
    cin >> n;
    unordered_map<int, int> freq;

    for (int i=0; i<n; i++){
        cin >> a;
        freq[a]++;
    }
    for (auto [key, value]: freq){
        pairs += value/2;
    }
    cout << pairs << endl;
    return 0;
}