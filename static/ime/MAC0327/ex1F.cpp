#include <bits/stdc++.h>
#define endl '\n'

using namespace std;

int main() {
    ios_base::sync_with_stdio(false); cin.tie(NULL); cout.tie(NULL);
    string s;
    cin >> s;
    int count = 1, max_count = 1;
    for (int i = 1; i < s.size(); i++) {
        if (s[i] == s[i - 1])
            count++;
        else
            count = 1;
        max_count = max(max_count, count);
    }
    cout << max_count << endl;
}