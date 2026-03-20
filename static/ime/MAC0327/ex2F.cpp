#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long
#define TEMPERATURA_MAXIMA 200001

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);
    
    int n, k, q;
    cin >> n >> k >> q;
    vector<int> diff(TEMPERATURA_MAXIMA + 1, 0);
    for (int i = 0; i < n; i++) {
        int l, r;
        cin >> l >> r;
        diff[l]++;
        diff[r + 1]--;
    }
    vector<int> prefix(TEMPERATURA_MAXIMA + 1, 0);
    int cnt = 0;
    for (int i = 1; i < TEMPERATURA_MAXIMA; i++) { cnt += diff[i]; prefix[i] = prefix[i - 1] + (cnt >= k); }
    for (int i = 0; i < q; i++) {
        int a, b;
        cin >> a >> b;
        cout << prefix[b] - prefix[a - 1] << endl;
    }

}
