export default {
    "*": {
        theme: {
            footer: false,
            toc: true,
            pagination: false
        }
    },
    index: {
        title: "HomePage",
        theme: {
            sidebar: true,
            footer: false,
            toc: true,
            pagination: false
        }
    },
    '---': {
        type: 'separator'
    },
    quick_start: "Quick Start",
    contact: "Contact Us",
    hackbot: {
        title: "Hackbot CI",
        display: "hidden"
    },
    github_link: {
        title: "Report an Issue (Github)",
        href: "https://github.com/GatlingX/hackbot_ci/issues",
        newWindow: true
    },
    company: {
        title: 'About GatlingX',
        type: 'menu',
        items: {
          about: {
            title: 'About',
            href: '/about'
          },
          contact: {
            title: 'Contact Us',
            href: 'mailto:hello@gatlingx.com'
          }
        }
      }
}