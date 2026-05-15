using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using WebApp.Models;
using WebApp.Services;

namespace WebApp.Controllers;

public class AuthController : Controller
{
    CeramicContext context;
    public AuthController(CeramicContext context)
    {
        this.context = context;
    }
    public IActionResult Register()
    {
        return View();
    }

    [HttpPost]
    public IActionResult Register(RegisterModel obj)
    {
        if (ModelState.IsValid)
        {
            Member member = new Member()
            {
                Id = Guid.NewGuid().ToString().Replace("-", string.Empty),
                Name = obj.Name,
                GivenName = obj.GivenName,
                Surname = obj.Surname,
                Email = obj.Email,
                Password = Helper.Hash(obj.Email, obj.Password)
            };
            context.Members.Add(member);
            int ret = context.SaveChanges();
            TempData["Msg"] = "Register Success";
            if (ret > 0) return Redirect("/auth/login");
            ModelState.AddModelError("Error", "Register Failed");
        }
        return View(obj);
    }
    [HttpPost, Authorize]
    public async Task<IActionResult> Logout()
    {
        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        return Redirect("/auth/login");
    }
    public IActionResult Denied()
    {
        return View();
    }
    public IActionResult Login()
    {
        return View();
    }
    [HttpPost]
    public async Task<IActionResult> Login(LoginModel obj)
    {
        if (ModelState.IsValid)
        {
            Member? member = context.Members.Where(p => p.Email == obj.Email && p.Password == Helper.Hash(obj.Email, obj.Password)).FirstOrDefault();
            if (member != null)
            {
                List<Claim> claims = new List<Claim>()
                    {
                        new Claim(ClaimTypes.NameIdentifier, member.Id),
                        new Claim(ClaimTypes.Name, member.Name),
                        new Claim(ClaimTypes.GivenName, member.GivenName),
                        new Claim(ClaimTypes.Email, member.Email),
                        new Claim(ClaimTypes.Role, member.Role.ToString()),
                    };
                if (member.Surname != null) claims.Add(new Claim(ClaimTypes.Surname, member.Surname));
                ClaimsIdentity identity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
                ClaimsPrincipal principal = new ClaimsPrincipal(identity);
                AuthenticationProperties properties = new AuthenticationProperties { IsPersistent = obj.Remember };
                await HttpContext.SignInAsync(principal, properties);
                return Redirect("/auth");
            }
            ModelState.AddModelError("Error", "Login Failed");
        }
        return View(obj);
    }

    [Authorize]
    public IActionResult Index()
    {
        return View();
    }
}
