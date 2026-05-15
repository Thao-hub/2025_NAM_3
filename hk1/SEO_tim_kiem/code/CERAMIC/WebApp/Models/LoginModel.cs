namespace WebApp.Models;
public class LoginModel
{
    public string Email {get; set; } = null!;
    public string Password {get; set; } = null!;
    public bool Remember {get; set; }
}