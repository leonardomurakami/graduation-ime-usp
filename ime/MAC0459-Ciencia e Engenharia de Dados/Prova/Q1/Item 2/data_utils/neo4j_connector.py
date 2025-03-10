from neo4j import GraphDatabase

class Neo4jConnector:
  def __init__(self, url, user, password):
    self.driver = GraphDatabase.driver(url, auth=(user, password))
  
  def close(self):
    self.driver.close()

  def query(self, query, db=None):
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.driver.session(database=db) if db is not None else self.driver.session() 
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        return response

  def create_occurence(self, occurence):
    with self.driver.session() as session:
      created = session.write_transaction(self._create_occurence, occurence)
    print(created)

  def create_manufacturer(self, manufacturer):
    with self.driver.session() as session:
      created = session.write_transaction(self._create_manufacturer, manufacturer)
    print(created)
  
  def create_aircraft(self, aircraft):
    with self.driver.session() as session:
      created = session.write_transaction(self._create_aircraft, aircraft)
    print(created)

  def create_aircraft_damage(self, aircraft_damage):
    with self.driver.session() as session:
      created = session.write_transaction(self._create_aircraft_damage, aircraft_damage)
    print(created)

  def create_consequence(self, consequence):
    with self.driver.session() as session:
      created = session.write_transaction(self._create_consequence, consequence)
    print(created)

  @staticmethod
  def _create_occurence(tx, occurence):
    result = tx.run(f"""
      MERGE (a:Occurence {{
        code: '{occurence.code}',
        date: '{occurence.date}',
        state: '{occurence.state}',
        city: '{occurence.city}',
        category: '{occurence.category}'
      }})
    """
    f"""
      RETURN a.code + ' - ' + a.date + ' AT ' + a.state + ' ' + a.city
    """
    )
    return result.single()[0]

  @staticmethod
  def _create_manufacturer(tx, manufacturer):
    result = tx.run(f"""
      MERGE (a:Manufacturer {{
        name: '{manufacturer.name}',
        country: '{manufacturer.country}'
      }})
    """
    f"""
      RETURN a.name + ' - ' + a.country
    """
    )
    return result.single()[0]

  @staticmethod
  def _create_aircraft(tx, aircraft):
    result = tx.run(f"""
      MERGE (a:Aircraft {{
        registration_code: '{aircraft.registration_code}',
        aircraft_type: '{aircraft.aircraft_type}',
        manufacturer_name: '{aircraft.manufacturer}',
        model: '{aircraft.model}',
        motor_type: '{aircraft.motor_type}',
        motor_quantity: '{aircraft.motor_quantity}',
        seats: '{aircraft.seats}',
        fabrication_year: '{aircraft.fabrication_year}',
        flight_distance: '{aircraft.flight_distance}'
      }})
    """
    f"""
      RETURN a.registration_code + ' - ' + a.model
    """
    )
    tx.run(
        f"""
          MATCH (a:Aircraft), (m:Manufacturer)
          WHERE a.registration_code = '{aircraft.registration_code}' 
          AND m.name = '{aircraft.manufacturer}'
          MERGE (a)<-[r:manufactured]-(m)
        """
    )


    return result.single()[0]

  @staticmethod
  def _create_aircraft_damage(tx, aircraft_damage):
    result = tx.run(f"""
      MERGE (a:Damage {{
        occurence_code: '{aircraft_damage.occurence_code}',
        registration_code: '{aircraft_damage.registration_code}',
        operation_type: '{aircraft_damage.operation_type}',
        operation_phase: '{aircraft_damage.operation_phase}',
        damage: '{aircraft_damage.damage}',
        fatalities: '{aircraft_damage.fatalities}'
      }})
    """
    f"""
      RETURN a.occurence_code + ' - ' + a.registration_code
    """
    )
    tx.run(
        f"""
          MATCH (d:Damage), (a:Aircraft)
          WHERE d.registration_code = '{aircraft_damage.registration_code}' 
          AND d.occurence_code = '{aircraft_damage.occurence_code}' 
          AND a.registration_code = '{aircraft_damage.registration_code}'
          MERGE (d)-[r:damaged]->(a)
        """
    )
    tx.run(
        f"""
          MATCH (d:Damage), (o:Occurence)
          WHERE d.registration_code = '{aircraft_damage.registration_code}' 
          AND d.occurence_code = '{aircraft_damage.occurence_code}'  
          AND o.code = '{aircraft_damage.occurence_code}'
          MERGE (o)-[r:caused]->(d)
        """
    )
    return result.single()[0]

  @staticmethod
  def _create_consequence(tx, consequence):
    result = tx.run(f"""
      MERGE (a:Consequence {{
        code: '{consequence.code}',
        occurence_code: '{consequence.occurence_code}',
        signature_day: '{consequence.signature_day}',
        forwarding_day: '{consequence.forwarding_day}',
        feedback_day: '{consequence.feedback_day}',
        feedback_addressee: '{consequence.feedback_addressee}'
      }})
    """
    f"""
      RETURN a.code + ' - ' + a.occurence_code
    """
    )
    tx.run(
        f"""
          MATCH (c:Consequence), (o:Occurence)
          WHERE c.code = '{consequence.code}' 
          AND o.code = '{consequence.occurence_code}'
          MERGE (o)-[r:consequence]->(c)
        """
    )
    return result.single()[0]
