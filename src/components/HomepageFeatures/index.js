import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Portfólio Acadêmico',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        Esta documentação apresenta uma coleção de projetos e trabalhos 
        desenvolvidos durante minha graduação no IME-USP.
      </>
    ),
  },
  {
    title: 'Organização por Disciplinas',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Navegar pelos trabalhos é simples e intuitivo. Os projetos estão organizados
        por disciplinas e incluem todos os principais entregáveis e suas descrições.
      </>
    ),
  },
  {
    title: 'Documentação Técnica',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Cada projeto contém explicações técnicas detalhadas, incluindo código-fonte,
        análises e reflexões sobre o processo de desenvolvimento.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p className="text--responsive">{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}