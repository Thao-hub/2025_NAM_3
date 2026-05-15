using Microsoft.AspNetCore.Mvc;
using WebApp.Models;
namespace WebApp.Controllers;

public class HomeController : Controller
{
    const int Size = 32;
    CeramicContext context;
    public HomeController(CeramicContext context)
    {
        this.context = context;
    }
    public IActionResult Search(string q, int page = 1)
    {
        if(string.IsNullOrEmpty(q)) return Redirect("/");
        ViewBag.Categories = context.Categories.ToList();
        IQueryable<Article> query = context.Articles.Where(p => p.Title.Contains(q) || p.Description.Contains(q));
        if(query is null) return Redirect("/");
        int count = query.Count();
        if(count < 1) return Redirect("/");
        ViewBag.NumPages = (count - 1) / 16 + 1;
        return View(query.OrderByDescending(p => p.Id).Skip((page - 1) * 16).Take(16).ToList());
    }
    public IActionResult GoogleSearch()
    {
        return View();
    }
    public IActionResult Index(int page = 1)
    {
        ViewBag.Categories = context.Categories.ToList();
        //Native
        int count = context.Articles.Count();
        int numPages = (count - 1) / Size + 1;
        ViewBag.NumPages = numPages;
        return View(context.Articles.OrderByDescending(p => p.Id).Skip((page - 1) * Size).Take(Size).ToList());
    }
    [HttpGet("/home/category/{id}/{slug}.html")]
    public IActionResult Category(short id, int page = 1)
    {
        ViewBag.Category = context.Categories.Find(id);
        ViewBag.Categories = context.Categories.ToList();
        //Native
        IQueryable<Article> query = context.Articles.Where(p => p.CategoryId == id);
        int count = query.Count();
        int numPages = (count - 1) / 8 + 1;
        ViewBag.NumPages = numPages;
        return View(query.OrderByDescending(p => p.Id).Skip((page - 1) * 8).Take(8).ToList());
    }
    [HttpGet("/home/details/{id}/{slug}.html")]
    public IActionResult Details(int id, int page = 1)
    {
        Article? obj = context.Articles.Find(id);
        if (obj is null) return Redirect("/");
        ViewBag.Categories = context.Categories.ToList();
        ViewBag.Article = obj;
        ViewBag.Category = context.Categories.Find(obj.CategoryId);
        //Naive
        IQueryable<Article> query = context.Articles.Where(p => p.CategoryId == obj.CategoryId && p.Id != id);
        int count = query.Count();
        int numPages = (count - 1) / 8 + 1;
        ViewBag.NumPages = numPages;
        return View(query.OrderByDescending(p => p.Id).Skip((page - 1) * 8).Take(8).ToList());
    }
}