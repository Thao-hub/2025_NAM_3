
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.EntityFrameworkCore;
using WebApp.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme).AddCookie(p => {
    p.LoginPath = "/auth/login";
    p.LogoutPath = "/auth/logout";
    p.AccessDeniedPath = "/auth/denied";
    p.ExpireTimeSpan = TimeSpan.FromDays(30);
});

builder.Services.AddDbContext<CeramicContext>(p => p.UseSqlServer(builder.Configuration.GetConnectionString("Ceramic")));
builder.Services.AddMvc();
var app = builder.Build();

// app.MapGet("/", () => "Hello World!");
app.UseStaticFiles();
app.MapDefaultControllerRoute();
app.Run();
