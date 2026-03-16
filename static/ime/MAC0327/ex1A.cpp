#include <bits/stdc++.h>
using namespace std;

#define endl '\n'
#define ll long long

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);

    int t, q, s, k;
    cin >> t;

    for (int i = 0; i < t; i++) {
        cin >> q;

        deque<int> arr;
        ll sum_arr = 0;
        ll rizz = 0;
        bool reversed = false;

        for (int j = 0; j < q; j++) {
            cin >> s;
            ll n = (ll)arr.size();
            if (s == 1) {
                ll back;
                if (!reversed) {
                    back = arr.back();
                    arr.push_front(back);
                    arr.pop_back();
                } else {
                    back = arr.front();
                    arr.push_back(back);
                    arr.pop_front();
                }
                rizz += sum_arr - n * back;
            } else if (s == 2) {
                rizz = (n + 1) * sum_arr - rizz;
                reversed = !reversed;
            } else {
                cin >> k;
                if (!reversed) arr.push_back(k);
                else arr.push_front(k);
            
                rizz += (n + 1) * k;
                sum_arr += k;
            }
            cout << rizz << endl;;
        }
    }
    return 0;
}
