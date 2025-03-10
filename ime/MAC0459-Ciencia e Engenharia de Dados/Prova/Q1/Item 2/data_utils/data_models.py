class Manufacturer:
  def __init__(
    self,
    name,
    country
  ):
    self.name = name
    self.country = country

class Aircraft:
  def __init__(
    self,
    registration_code,
    aircraft_type,
    manufacturer_name,
    model,
    motor_type,
    motor_quantity,
    seats,
    fabrication_year,
    flight_distance
  ):
    self.registration_code = registration_code
    self.aircraft_type = aircraft_type
    self.model = model
    self.motor_type = motor_type
    self.motor_quantity = motor_quantity
    self.seats = seats
    self.fabrication_year = fabrication_year
    self.manufacturer = manufacturer_name
    self.flight_distance = flight_distance
    
class AircraftDamage:
  def __init__(
    self,
    occurence_code,
    registration_code,
    operation_type,
    operation_phase,
    damage,
    fatalities
  ):
    self.occurence_code = occurence_code
    self.registration_code = registration_code
    self.operation_type = operation_type
    self.operation_phase = operation_phase
    self.damage = damage
    self.fatalities = fatalities

class Occurence:
  def __init__(
    self,
    code,
    date,
    state,
    city,
    category
  ):
    self.code = code
    self.date = date
    self.state = state
    self.city = city
    self.category = category

class Consequence:
  def __init__(
    self,
    code,
    occurence_code,
    signature_day,
    forwarding_day,
    feedback_day,
    feedback_addressee
  ):
    self.code = code
    self.occurence_code = occurence_code
    self.signature_day = signature_day
    self.forwarding_day = forwarding_day
    self.feedback_day = feedback_day
    self.feedback_addressee = feedback_addressee
