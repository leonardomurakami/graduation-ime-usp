#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long
#define MODULO 1000000007

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);
    
    int n, x;
    cin >> n >> x;
    vector<int> coins(n);
    for (int i = 0; i < n; i++) cin >> coins[i];

    vector<ll> dsum(x + 1, 0);
    dsum[0] = 1;

    for (int i = 1; i <= x; i++) {
        for (int coin : coins) {
            if (i - coin >= 0) dsum[i] = (dsum[i] + dsum[i - coin]) % MODULO;
        }
    }

    cout << dsum[x] << endl;
}
