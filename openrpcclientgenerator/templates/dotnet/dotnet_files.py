""".NET project file templates."""

solution = """
Microsoft Visual Studio Solution File, Format Version 12.00
Project("{{{id}}}") = "{name}", "{name}\\{name}.csproj", "{{{uuid}}}"
EndProject
Global
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tDebug|Any CPU = Debug|Any CPU
\t\tRelease|Any CPU = Release|Any CPU
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t{{{uuid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
\t\t{{{uuid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU
\t\t{{{uuid}}}.Release|Any CPU.ActiveCfg = Release|Any CPU
\t\t{{{uuid}}}.Release|Any CPU.Build.0 = Release|Any CPU
\tEndGlobalSection
EndGlobal
"""

csproj = """
<Project Sdk="Microsoft.NET.Sdk">

    <PropertyGroup>
        <TargetFramework>net6.0</TargetFramework>
        <RootNamespace>{name}</RootNamespace>
        <PackageId>{name}</PackageId>
        <Version>{version}</Version>
        <Authors>{authors}</Authors>
        <Description>{description}</Description>
        <Copyright>Copyright © {year} {copyright_holder}</Copyright>
        <LangVersion>9</LangVersion>
    </PropertyGroup>

    <ItemGroup>
      <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
    </ItemGroup>

    <ItemGroup>
      <PackageReference Include="JsonRpcClient" Version="5.1.0" >
        <SpecificVersion>True</SpecificVersion>
      </PackageReference>
    </ItemGroup>

</Project>
"""
