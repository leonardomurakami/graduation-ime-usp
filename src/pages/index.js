import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Explorar Projetos Acadêmicos
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Portfólio de projetos acadêmicos desenvolvidos durante a graduação no IME-USP">
      <HomepageHeader />
      <main>
        <section className={styles.aboutSection}>
          <div className="container">
            <div className="row">
              <div className="col col--8 col--offset-2">
                <Heading as="h2" className={styles.sectionTitle}>
                  Sobre este Portfólio
                </Heading>
                <p className="text--responsive">
                  Bem-vindo ao meu portfólio acadêmico! Este site reúne os principais trabalhos e projetos 
                  que desenvolvi durante minha graduação no Instituto de Matemática e Estatística da 
                  Universidade de São Paulo (IME-USP).
                </p>
                <p className="text--responsive">
                  Aqui você encontrará uma documentação organizada dos meus entregáveis acadêmicos, 
                  incluindo códigos, análises, relatórios e projetos práticos. Cada projeto contém 
                  uma descrição detalhada do problema abordado, a metodologia utilizada e os resultados obtidos.
                </p>
                <p className="text--responsive">
                  Este portfólio serve tanto como registro pessoal da minha jornada acadêmica quanto 
                  como demonstração das habilidades e conhecimentos que adquiri ao longo da graduação.
                </p>
              </div>
            </div>
          </div>
        </section>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}