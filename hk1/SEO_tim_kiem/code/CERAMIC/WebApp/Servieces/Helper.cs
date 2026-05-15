using System.Security.Cryptography;
using System.Text;

namespace WebApp.Services;

public static class Helper
{
    public static int GetPage(this HttpContext context, string name)
    {
        string? query = context.Request.Query[name];
        if(string.IsNullOrEmpty(query)) return 1;
        return Convert.ToInt32(query);
    }
    public static string RandomString(int len)
    {
        char[] arr = new char[len];
        Random rand = new Random();
        string pattent = "0123456789abcdefghiklmnopqrstuvwxyz";
        for(int i = 0; i < len; i++)
        {
            arr[i] = pattent[rand.Next(0, pattent.Length)];
        }
        return string.Join(string.Empty, arr);
    }
    public static byte[] Hash(string plaintext)
    {
        using(HashAlgorithm algorithm = SHA512.Create())
        {
            return algorithm.ComputeHash(Encoding.ASCII.GetBytes(plaintext));
        }
    }
    public static byte[] Hash(string salt, string password)
    {
        return Hash(salt + "$@!?" + password);
    }
}