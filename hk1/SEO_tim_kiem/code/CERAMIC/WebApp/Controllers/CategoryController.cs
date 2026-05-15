using Microsoft.AspNetCore.Mvc;
using WebApp.Models;
using WebApp.Services;

namespace WebApp.Controllers;
public class CategoryController : Controller
{
    CeramicContext context;
    public CategoryController(CeramicContext context)
    {
        this.context = context;
    }
    public IActionResult Index()
    {
        return View(context.Categories.ToList());
    }
    public IActionResult Add()
    {
        return View();
    }
    [HttpPost]
    public IActionResult Add(Category obj, IFormFile f)
    {
        ModelState.Remove(nameof(obj.ImageUrl));
        if (ModelState.IsValid && f != null)
        {
            string root = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "images");
            string ext = Path.GetExtension(f.FileName);
            string imagesUrl = Helper.RandomString(16 - ext.Length) + ext;
            using(Stream stream = new FileStream(Path.Combine(root, imagesUrl), FileMode.Create))
            {
                f.CopyTo(stream);
            }
            obj.ImageUrl = imagesUrl;
            context.Categories.Add(obj);
            if (context.SaveChanges() > 0)
            {
                return Redirect("/category");
            }
            ModelState.AddModelError("Error", "Insert Failed"); 
        }
        return View();
    }
}