#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);
    
    int n, x, q, m;
    vector<int> shops;
    cin >> n;
    for (int i=0; i<n; i++){
        cin >> x;
        shops.push_back(x);
    }
    sort(shops.begin(), shops.end());
    cin >> q;
    for (int i=0; i<q; i++){
        cin >> m;
        cout << (int)(upper_bound(shops.begin(), shops.end(), m) - shops.begin()) << endl;
    }
    return 0;
}