#include <bits/stdc++.h>
using namespace std;

#define endl '\n'

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);

    int t, q, s, k;
    cin >> t;

    for (int i = 0; i < t; i++) {
        cin >> q;

        deque<int> arr;
        long long sum_arr = 0;
        long long rizz = 0;
        bool reversed = false;

        for (int j = 0; j < q; j++) {
            cin >> s;
            long long n = (long long)arr.size();

            if (s == 1) {
                long long back = reversed ? arr.front() : arr.back();
                rizz += sum_arr - n * back;
                if (reversed) {
                    arr.push_front(arr.back());
                    arr.pop_back();
                } else {
                    arr.push_back(arr.front());
                    arr.pop_front();
                }
            } else if (s == 2) {
                rizz = (n + 1) * sum_arr - rizz;
                reversed = !reversed;
            } else {
                cin >> k;
                if (reversed) arr.push_back(k);
                else arr.push_front(k);
            
                rizz += (n + 1) * k;
                sum_arr += k;
            }
            cout << rizz << endl;;
        }
    }

    return 0;
}
