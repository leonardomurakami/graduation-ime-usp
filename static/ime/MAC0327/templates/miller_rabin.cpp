ll fast_pow(ll base, ll exp, ll mod) {
    if (exp == 0) return 1;
    if (exp == 1) return base;
    ll res = fast_pow(base, exp / 2, mod);
    res = (res * res) % mod;
    if (exp % 2 == 1) res = (res * base) % mod;
    return res;
}

bool is_prime(ll n) {
    static const ll witnesses[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    if (n < 2) return false;
    int s = __builtin_ctzll(n - 1);
    ll d = (n - 1) >> s;
    for (ll a : witnesses) {
        if (n == a) return true;
        ll p = fast_pow(a, d, n), i = s;
        while (p != 1 && p != n-1 && a%n && i--)
            p = (p * p) % n;
        if (p != n-1 && i < 0) return false;
    }
    return true;
}