using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using WebApp.Models;

namespace WebApp.Controllers;

[Authorize(Roles = "Admin")]

public class MemberController : Controller
{
    CeramicContext context;
    public MemberController(CeramicContext context)
    {
        this.context = context;
    }
    public IActionResult Index()
    {
        return View(context.Members.ToList());
    }
}